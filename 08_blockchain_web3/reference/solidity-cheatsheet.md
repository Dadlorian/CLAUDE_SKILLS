# Solidity Cheat Sheet

## Data Types
```solidity
// Value Types
bool public isActive = true;
int256 public signedNumber = -123;
uint256 public unsignedNumber = 123;
address public userAddress = 0x...;
bytes32 public fixedBytes;
string public text = "Hello";

// Reference Types
uint[] public dynamicArray;
uint[10] public fixedArray;
mapping(address => uint) public balances;
struct User { address addr; uint balance; }
```

## Function Modifiers
```solidity
public      // Callable from anywhere
external    // Only externally (saves gas)
internal    // Only this + inherited
private     // Only this contract
view        // Reads state, no modification
pure        // No state access
payable     // Can receive ETH
```

## Common Patterns
```solidity
// Checks-Effects-Interactions
function withdraw() external {
    uint amount = balances[msg.sender]; // Checks
    balances[msg.sender] = 0;           // Effects
    payable(msg.sender).transfer(amount); // Interactions
}

// Require statements
require(amount > 0, "Zero amount");
require(msg.sender == owner, "Not owner");

// Custom errors (0.8.4+)
error Unauthorized();
if (msg.sender != owner) revert Unauthorized();

// Events
event Transfer(address indexed from, address indexed to, uint value);
emit Transfer(msg.sender, to, amount);
```

## Gas Optimization
```solidity
uint256 public constant MAX = 1000;     // Compile-time
uint256 public immutable DEPLOYED_AT;   // Constructor
uint256 private cached;                 // Cache storage reads
unchecked { ++i; }                      // Skip overflow checks
```
