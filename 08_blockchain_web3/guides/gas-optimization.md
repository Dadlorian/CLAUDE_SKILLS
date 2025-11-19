# Gas Optimization Guide

Comprehensive guide to minimizing gas costs in smart contracts.

## Storage Optimization (Most Important)

Storage operations are the most expensive. Optimize storage first.

### 1. Pack Storage Variables

**Cost**: Reading/writing storage slots costs 20,000/5,000 gas. Pack variables into 32-byte slots.

```solidity
// ❌ BAD: Uses 3 storage slots (63,000 gas)
contract Unoptimized {
    uint128 a;  // Slot 0
    uint256 b;  // Slot 1
    uint128 c;  // Slot 2
}

// ✅ GOOD: Uses 2 storage slots (42,000 gas) - 33% savings
contract Optimized {
    uint128 a;  // Slot 0
    uint128 c;  // Slot 0 (packed)
    uint256 b;  // Slot 1
}

// ✅ BETTER: Strategic packing
contract BestPacking {
    uint128 value1;
    uint128 value2;  // Same slot
    uint64 timestamp;
    uint64 counter;
    address owner;   // All in slot 2 (160 bits + 64 + 64 = 288 bits < 256)
    bool active;     // Slot 2
}
```

**Packing Rules**:
- `uint256` = 32 bytes (full slot)
- `uint128` = 16 bytes (2 per slot)
- `uint64` = 8 bytes (4 per slot)
- `address` = 20 bytes
- `bool` = 1 byte (32 per slot theoretically, but pack with larger types)

### 2. Use `immutable` for Constructor-Set Constants

**Cost**: Reading immutable costs 3 gas vs 2100 gas for storage

```solidity
// ❌ BAD: Storage read (2100 gas per read)
contract Unoptimized {
    address public owner;
    uint256 public deploymentTime;

    constructor() {
        owner = msg.sender;
        deploymentTime = block.timestamp;
    }
}

// ✅ GOOD: Immutable (3 gas per read)
contract Optimized {
    address public immutable owner;
    uint256 public immutable deploymentTime;

    constructor() {
        owner = msg.sender;
        deploymentTime = block.timestamp;
    }
}
```

### 3. Use `constant` for Compile-Time Constants

**Cost**: Inlined at compile time (no storage, no gas)

```solidity
// ❌ BAD: Storage variable
uint256 public maxSupply = 10000;

// ✅ GOOD: Constant (inlined, free)
uint256 public constant MAX_SUPPLY = 10000;
```

### 4. Cache Storage Reads

**Cost**: Each storage read costs 2100 gas (warm) or 100 gas (cached in memory)

```solidity
// ❌ BAD: Multiple storage reads (6300 gas)
function calculateTotal() external view returns (uint256) {
    return (storageValue * storageValue) + storageValue;
    // Reads storageValue 3 times from storage
}

// ✅ GOOD: Cache in memory (2100 + 3 + 3 gas)
function calculateTotal() external view returns (uint256) {
    uint256 cached = storageValue; // Read once from storage
    return (cached * cached) + cached; // Use cached value
}
```

### 5. Delete Variables to Get Gas Refunds

**Refund**: Setting storage to zero refunds 15,000 gas

```solidity
// ✅ GOOD: Delete to get refund
function withdraw() external {
    uint256 amount = balances[msg.sender];
    delete balances[msg.sender]; // 15,000 gas refund
    payable(msg.sender).transfer(amount);
}
```

## Function Optimization

### 6. Use `calldata` Instead of `memory` for Read-Only Parameters

**Cost**: calldata is 3 gas vs memory is 3+ gas plus copying costs

```solidity
// ❌ BAD: Copies to memory
function processData(uint256[] memory data) external {
    // Uses ~500 gas to copy array to memory
}

// ✅ GOOD: Read directly from calldata
function processData(uint256[] calldata data) external {
    // No copy, reads directly (saves ~500 gas for 10-element array)
}
```

### 7. Use `external` Instead of `public` When Possible

**Cost**: external saves ~200-500 gas by not copying parameters

```solidity
// ❌ BAD: Public function (can be called internally and externally)
function transfer(address to, uint256 amount) public {
    // Costs more gas
}

// ✅ GOOD: External (only called externally)
function transfer(address to, uint256 amount) external {
    // Saves gas by not creating internal call infrastructure
}
```

### 8. Mark Functions as `view`/`pure` When Possible

Helps compiler optimize and signals intent.

```solidity
// ✅ GOOD: Compiler optimizes view/pure functions
function calculateFee(uint256 amount) external pure returns (uint256) {
    return amount * 3 / 1000; // No state reads/writes
}

function getBalance(address user) external view returns (uint256) {
    return balances[user]; // Only reads state
}
```

## Arithmetic Optimization

### 9. Use `unchecked` for Safe Arithmetic

**Cost**: Saves ~20-40 gas per operation (Solidity 0.8+)

```solidity
// ❌ BAD: Unnecessary overflow checks
function increment(uint256 value) external pure returns (uint256) {
    return value + 1; // Includes overflow check
}

// ✅ GOOD: Unchecked when provably safe
function increment(uint256 value) external pure returns (uint256) {
    unchecked {
        return value + 1; // No overflow check (saves ~20 gas)
    }
}

// ✅ GOOD: Real-world example
function processArray(uint256[] calldata data) external {
    uint256 length = data.length;
    for (uint256 i = 0; i < length; ) {
        // Process data[i]

        unchecked {
            ++i; // Can't overflow (array length < 2^256)
        }
    }
}
```

### 10. Use Prefix Increment (++i) Instead of Postfix (i++)

**Cost**: Saves ~5 gas

```solidity
// ❌ BAD: Postfix (stores temporary)
for (uint256 i = 0; i < length; i++) { }

// ✅ GOOD: Prefix
for (uint256 i = 0; i < length; ++i) { }

// ✅ BETTER: Prefix + unchecked
for (uint256 i = 0; i < length; ) {
    // Loop body
    unchecked { ++i; }
}
```

### 11. Avoid Zero to Non-Zero Storage Writes

**Cost**: Writing non-zero to zero costs 20,000 gas vs 5,000 gas for non-zero to non-zero

```solidity
// ✅ GOOD: Initialize to 1 instead of 0 for frequently toggled values
uint256 private constant NOT_ENTERED = 1;
uint256 private constant ENTERED = 2;
uint256 private status = NOT_ENTERED;

modifier nonReentrant() {
    require(status != ENTERED);
    status = ENTERED;
    _;
    status = NOT_ENTERED; // 5,000 gas (non-zero to non-zero)
}
```

## Data Structure Optimization

### 12. Use Mappings Instead of Arrays (When Possible)

**Cost**: Mappings have O(1) lookup, arrays have O(n)

```solidity
// ❌ BAD: Array lookup (expensive for large arrays)
address[] public users;
function isUser(address user) external view returns (bool) {
    for (uint i = 0; i < users.length; i++) {
        if (users[i] == user) return true;
    }
    return false;
}

// ✅ GOOD: Mapping lookup (constant time)
mapping(address => bool) public isUser;
```

### 13. Use Bytes Instead of String (When Possible)

**Cost**: bytes is more efficient for non-UTF8 data

```solidity
// ❌ BAD: String (slightly more expensive)
string public name;

// ✅ GOOD: bytes32 for fixed-length strings
bytes32 public name; // Stores up to 32 characters
```

### 14. Batch Operations

**Cost**: Amortize fixed costs across multiple operations

```solidity
// ❌ BAD: Individual transfers
function transferMultiple(address[] memory recipients, uint256[] memory amounts) {
    for (uint i = 0; i < recipients.length; i++) {
        transfer(recipients[i], amounts[i]); // External call overhead each time
    }
}

// ✅ GOOD: Batch transfer
function batchTransfer(address[] calldata recipients, uint256[] calldata amounts) external {
    require(recipients.length == amounts.length);
    for (uint i = 0; i < recipients.length; ) {
        _transfer(msg.sender, recipients[i], amounts[i]); // Internal call
        unchecked { ++i; }
    }
}
```

## Custom Errors (Solidity 0.8.4+)

### 15. Use Custom Errors Instead of Require Strings

**Cost**: Saves ~50 gas per revert

```solidity
// ❌ BAD: String error messages (expensive)
require(amount > 0, "Amount must be greater than zero");
require(balance >= amount, "Insufficient balance");

// ✅ GOOD: Custom errors (cheaper)
error ZeroAmount();
error InsufficientBalance(uint256 requested, uint256 available);

if (amount == 0) revert ZeroAmount();
if (balance < amount) revert InsufficientBalance(amount, balance);
```

## Event Optimization

### 16. Use Indexed Parameters Wisely

**Cost**: Each indexed parameter costs ~375 gas extra

```solidity
// ❌ BAD: Too many indexed parameters
event Transfer(
    address indexed from,
    address indexed to,
    uint256 indexed amount,  // Indexed uint256 is wasteful (already in data)
    uint256 indexed timestamp
);

// ✅ GOOD: Index addresses, not values
event Transfer(
    address indexed from,
    address indexed to,
    uint256 amount,
    uint256 timestamp
);
```

## Advanced Optimization Patterns

### 17. Bit Packing for Booleans

**Cost**: Store 256 booleans in one storage slot

```solidity
// ❌ BAD: Each bool uses a storage slot
mapping(uint256 => bool) public claimed;

// ✅ GOOD: Bitmap for booleans
uint256[10] private claimedBitMap; // 2560 booleans in 10 slots

function setClaimed(uint256 index) internal {
    uint256 wordIndex = index / 256;
    uint256 bitIndex = index % 256;
    claimedBitMap[wordIndex] |= (1 << bitIndex);
}

function isClaimed(uint256 index) public view returns (bool) {
    uint256 wordIndex = index / 256;
    uint256 bitIndex = index % 256;
    return (claimedBitMap[wordIndex] >> bitIndex) & 1 == 1;
}
```

### 18. Short-Circuit Evaluation

**Cost**: Order conditions by likelihood and cost

```solidity
// ❌ BAD: Expensive check first
require(expensiveCheck() && cheapCheck());

// ✅ GOOD: Cheap check first (short-circuits if fails)
require(cheapCheck() && expensiveCheck());
```

### 19. Avoid Redundant Checks

```solidity
// ❌ BAD: Redundant checks
function transfer(address to, uint256 amount) external {
    require(to != address(0)); // Check 1
    require(amount > 0);        // Check 2
    _transfer(msg.sender, to, amount); // Checks again inside
}

function _transfer(address from, address to, uint256 amount) internal {
    require(to != address(0)); // Duplicate check!
    require(amount > 0);        // Duplicate check!
    // Transfer logic
}

// ✅ GOOD: Check once
function transfer(address to, uint256 amount) external {
    _transfer(msg.sender, to, amount); // Checks inside
}

function _transfer(address from, address to, uint256 amount) internal {
    require(to != address(0));
    require(amount > 0);
    // Transfer logic
}
```

### 20. Minimize Storage Writes in Loops

```solidity
// ❌ BAD: Write to storage every iteration
function badLoop(uint256[] calldata values) external {
    for (uint i = 0; i < values.length; i++) {
        storageValue += values[i]; // 5000 gas per iteration
    }
}

// ✅ GOOD: Accumulate in memory, write once
function goodLoop(uint256[] calldata values) external {
    uint256 accumulated;
    for (uint i = 0; i < values.length; ) {
        accumulated += values[i]; // 3 gas per iteration
        unchecked { ++i; }
    }
    storageValue += accumulated; // 5000 gas once
}
```

## Compiler Optimizations

### 21. Enable Optimizer with Proper Runs

```javascript
// hardhat.config.js
module.exports = {
  solidity: {
    version: "0.8.23",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200, // Default (balances deployment and runtime costs)
        // runs: 1 for minimal deployment cost
        // runs: 1000+ for minimal runtime cost
      },
      viaIR: true, // Enable IR-based optimizer (more aggressive)
    },
  },
};
```

## Gas Benchmarking Example

```solidity
contract GasComparison {
    uint256 public value;

    // Unoptimized: ~43,000 gas
    function unoptimized(uint256[] memory data) public {
        for (uint256 i = 0; i < data.length; i++) {
            value = value + data[i];
        }
    }

    // Optimized: ~28,000 gas (35% savings)
    function optimized(uint256[] calldata data) external {
        uint256 cached = value;
        uint256 length = data.length;

        for (uint256 i = 0; i < length; ) {
            cached += data[i];
            unchecked { ++i; }
        }

        value = cached;
    }
}
```

## Gas Cost Reference

| Operation | Gas Cost |
|-----------|----------|
| Storage write (zero → non-zero) | 20,000 |
| Storage write (non-zero → non-zero) | 5,000 |
| Storage read (cold) | 2,100 |
| Storage read (warm) | 100 |
| Memory expansion | 3 + (words^2 / 512) |
| SLOAD (cold) | 2,100 |
| SSTORE (zero → non-zero) | 20,000 |
| CALL (cold) | 2,600 |
| CALL (warm) | 100 |
| LOG0 | 375 |
| LOG with indexed parameter | +375 per parameter |
| SHA3/KECCAK256 | 30 + 6 per word |

## Tools for Gas Optimization

### Foundry Gas Snapshot
```bash
forge snapshot
forge snapshot --diff
```

### Hardhat Gas Reporter
```bash
npx hardhat test --gas-reporter
```

### Gas Profiling
```solidity
contract GasTest is Test {
    function testGas_Transfer() public {
        uint256 gasBefore = gasleft();
        token.transfer(alice, 100);
        uint256 gasUsed = gasBefore - gasleft();
        console.log("Gas used:", gasUsed);
    }
}
```

## Optimization Checklist

Storage:
- [ ] Variables packed into 32-byte slots
- [ ] immutable used for constructor-set values
- [ ] constant used for compile-time values
- [ ] Storage reads cached in memory
- [ ] delete used to get gas refunds

Functions:
- [ ] calldata used for read-only arrays
- [ ] external used instead of public
- [ ] view/pure marked appropriately

Arithmetic:
- [ ] unchecked used for safe operations
- [ ] Prefix increment (++i) used
- [ ] Efficient loop patterns

Data Structures:
- [ ] Mappings used over arrays for lookups
- [ ] Batch operations implemented
- [ ] Bit packing for booleans

Errors & Events:
- [ ] Custom errors instead of strings
- [ ] Indexed parameters optimized

Compiler:
- [ ] Optimizer enabled
- [ ] Appropriate runs value set
- [ ] viaIR considered for complex contracts

---

**Remember**: Optimize for readability first, then optimize for gas. Always measure before and after optimization to confirm savings.
