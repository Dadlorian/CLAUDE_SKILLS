# Gas Optimization Guide

## Understanding Gas Costs

### Opcode Costs (Common)
- STOP: 0
- ADD/SUB: 3
- MUL/DIV: 5
- SLOAD (cold): 2100
- SLOAD (warm): 100
- SSTORE (new): 20000
- SSTORE (update): 5000
- CALL/DELEGATECALL: 700+

## Storage Optimization

### Packing Storage Variables
```solidity
// Bad: Uses 3 storage slots
contract BadPacking {
    uint256 a; // 32 bytes
    uint8 b;   // 32 bytes (wasted!)
    uint256 c; // 32 bytes
}

// Good: Uses 1 storage slot
contract GoodPacking {
    uint256 a;      // 32 bytes
    uint8 b;        // 1 byte
    uint8 c;        // 1 byte
    // 30 bytes unused but in same slot
}

// Best: Uses 2 storage slots efficiently
contract BestPacking {
    uint256 a;           // 32 bytes (slot 0)
    uint128 b;           // 16 bytes
    uint64 c;            // 8 bytes
    uint32 d;            // 4 bytes  (slot 1)
}
```

### Cache Storage Reads
```solidity
// Bad: Multiple SLOAD
function transfer(address[] calldata recipients, uint256[] calldata amounts) public {
    for (uint i = 0; i < recipients.length; i++) {
        balances[recipients[i]] += amounts[i]; // SLOAD every iteration
    }
}

// Good: Cache in memory
function transfer(address[] calldata recipients, uint256[] calldata amounts) public {
    mapping(address => uint256) storage balances_ = balances;
    for (uint i = 0; i < recipients.length; i++) {
        balances_[recipients[i]] += amounts[i]; // Reference doesn't SLOAD
    }
}
```

## Computation Optimization

### Use Bit Shifting
```solidity
// Bad: Uses MUL (5 gas)
uint256 result = amount * 2;
uint256 result = amount / 256;

// Good: Uses SHL/SHR (3 gas)
uint256 result = amount << 1;
uint256 result = amount >> 8;
```

### Avoid Unnecessary Calculations
```solidity
// Bad: Calls getPrice() multiple times
function processTokens(uint256[] calldata amounts) public {
    for (uint i = 0; i < amounts.length; i++) {
        uint256 price = getPrice(); // Called every iteration
        balances[i] = amounts[i] * price;
    }
}

// Good: Cache calculation
function processTokens(uint256[] calldata amounts) public {
    uint256 price = getPrice(); // Called once
    for (uint i = 0; i < amounts.length; i++) {
        balances[i] = amounts[i] * price;
    }
}
```

## Loop Optimization

### Increment/Decrement Efficiency
```solidity
// Bad: i++ uses 3 operations
for (uint i = 0; i < 10; i++) { }

// Better: ++i is cheaper (unchecked prefix increment)
for (uint i = 0; i < 10; ++i) { }

// Best: Unchecked increment (no overflow check)
for (uint i = 0; i < 10; ) {
    unchecked { ++i; }
}

// Optimal: Cache array length, reverse loop
function process(uint256[] calldata items) public {
    for (uint i = items.length; i > 0; ) {
        unchecked { --i; }
        // Process items[i]
    }
}
```

### Avoid Repeated Array Length Calls
```solidity
// Bad: Calls length multiple times
for (uint i = 0; i < array.length; i++) { }

// Good: Cache length
uint256 len = array.length;
for (uint i = 0; i < len; ) {
    unchecked { ++i; }
}
```

## Function Optimization

### Use Pure/View Modifiers
```solidity
// Bad: Can be pure but isn't
function add(uint256 a, uint256 b) public returns (uint256) {
    return a + b;
}

// Good: Pure function (no state access)
function add(uint256 a, uint256 b) public pure returns (uint256) {
    return a + b;
}
```

### Minimal Function Parameters
```solidity
// Bad: Large parameters cause stack issues
function complexFunction(
    address a, address b, address c, address d,
    uint256 e, uint256 f, uint256 g, uint256 h
) public {}

// Good: Use struct to pack parameters
struct Params {
    address a; address b; address c; address d;
    uint256 e; uint256 f; uint256 g; uint256 h;
}

function complexFunction(Params calldata params) public {}
```

## Error Messages Optimization

### Use Custom Errors (Solidity 0.8.4+)
```solidity
// Bad: Uses 43 bytes in bytecode
require(amount > 0, "Amount must be positive");

// Good: Uses 6 bytes with custom error
error InvalidAmount();
if (amount == 0) revert InvalidAmount();

// Gas saved: ~50 gas for revert message
```

## Delegation and Proxies

### Use EIP-2930 (Access Lists)
```javascript
// Without access list: Higher gas
const tx = {
  to: contract,
  data: callData,
  value: ethers.parseEther("0"),
};

// With access list: Lower gas
const tx = {
  to: contract,
  data: callData,
  value: ethers.parseEther("0"),
  accessList: [
    {
      address: contract,
      storageKeys: [
        '0x0000000000000000000000000000000000000000000000000000000000000000',
      ],
    },
  ],
};
```

## Solidity Assembly

### Use Assembly for Critical Functions
```solidity
// Pure Solidity (higher gas)
function safeMul(uint256 a, uint256 b) public pure returns (uint256) {
    if (a == 0) return 0;
    uint256 c = a * b;
    require(c / a == b);
    return c;
}

// Assembly (lower gas, but riskier)
function safeMulAssembly(uint256 a, uint256 b) public pure returns (uint256 c) {
    assembly {
        if a {
            c := mul(a, b)
            if iszero(eq(div(c, a), b)) {
                revert(0, 0)
            }
        }
    }
}
```

## Gas Profiling

### Using Hardhat to Profile
```bash
npx hardhat test --gas-report

# Output shows gas used per function
# Compare before/after optimizations
```

## Production Optimization Checklist

- [ ] Use storage-efficient packing
- [ ] Cache storage reads
- [ ] Use bit shifting where applicable
- [ ] Use custom errors (Solidity 0.8.4+)
- [ ] Optimize loops
- [ ] Use unchecked blocks where safe
- [ ] Profile gas consumption
- [ ] Compare optimization techniques
- [ ] Document gas-critical sections
- [ ] Monitor mainnet gas costs

---

**Key Takeaways**:
- Storage layout has huge impact
- Caching reads saves gas
- Bit operations cheaper than math
- Custom errors save bytecode
- Profile and test optimizations
- Balance readability with efficiency
