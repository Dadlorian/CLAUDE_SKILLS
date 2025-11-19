# Smart Contracts Reference

## What are Smart Contracts?

Smart contracts are self-executing digital agreements with terms written directly into code. They automatically execute when conditions are met, without intermediaries.

### Key Characteristics
- **Autonomous**: Execute without manual intervention
- **Deterministic**: Same input produces same output
- **Immutable**: Cannot be changed after deployment
- **Transparent**: Code is visible to all network participants
- **Irreversible**: Transactions cannot be undone (except through upgrades)

## Solidity Language Fundamentals

### Data Types

#### Value Types
```solidity
// Booleans
bool isActive = true;

// Integers (signed and unsigned)
uint256 amount = 1000;  // 0 to 2^256-1
int256 delta = -50;     // -(2^255) to 2^255-1
uint8, uint16, uint32... uint256
int8, int16, int32... int256

// Fixed-point numbers
fixed128x18 price = 1.5;  // Limited support

// Addresses (20 bytes)
address account = 0x1234...;
address payable wallet = payable(0x1234...);

// Bytes (fixed-size and dynamic)
bytes32 hash = 0xabcd...;
bytes memory data = new bytes(100);

// Strings
string memory message = "Hello";

// Enums
enum Status { Pending, Active, Completed }
```

#### Reference Types
```solidity
// Arrays
uint256[] memory dynamicArray;
uint256[10] storage fixedArray;
uint256[][] memory matrix;

// Structs
struct User {
  address wallet;
  uint256 balance;
  bool isActive;
}

// Mappings
mapping(address => uint256) balances;
mapping(address => mapping(address => uint256)) allowances;
```

### Functions

```solidity
// Function declaration
function transfer(address to, uint256 amount)
  public                    // visibility: public, internal, external, private
  payable                   // can receive ETH
  override                  // overrides parent function
  returns (bool)            // return type
{
  // Function body
  return true;
}

// View functions (don't modify state)
function balanceOf(address account)
  public
  view
  returns (uint256)
{
  return balances[account];
}

// Pure functions (don't read or modify state)
function add(uint256 a, uint256 b)
  public
  pure
  returns (uint256)
{
  return a + b;
}
```

### Modifiers

```solidity
// Create reusable condition checks
modifier onlyOwner() {
  require(msg.sender == owner, "Not owner");
  _;  // Continue function execution
}

modifier nonReentrant() {
  require(!locked, "No reentrancy");
  locked = true;
  _;
  locked = false;
}

// Usage
function withdraw()
  public
  onlyOwner
  nonReentrant
{
  // Only owner can call, protected from reentrancy
}
```

## Contract Lifecycle

### 1. Creation
```solidity
// Constructor runs once at deployment
constructor(address initialOwner) {
  owner = initialOwner;
  totalSupply = 1000000;
}
```

### 2. Interaction
```solidity
// Via transactions
contract.transfer(recipient, amount);

// Via calls (read-only)
contract.balanceOf(account);
```

### 3. State Management
```solidity
// Update state
balance[msg.sender] -= amount;
balance[recipient] += amount;

// Emit events for indexing
emit Transfer(msg.sender, recipient, amount);
```

### 4. Destruction (Optional)
```solidity
// Destroy contract and return funds
selfdestruct(payable(owner));  // Deprecated in Shanghai
```

## Events and Logging

### Event Declaration
```solidity
event Transfer(
  indexed address from,
  indexed address to,
  uint256 value
);

event SwapExactTokensForTokens(
  uint256 amountIn,
  uint256 amountOutMin,
  address[] path,
  address indexed to,
  uint256 deadline
);
```

### Emitting Events
```solidity
emit Transfer(msg.sender, recipient, amount);
```

### Indexing
- **Indexed parameters**: Stored in event topic, queryable efficiently
- **Non-indexed**: Stored in event data, requires scanning
- Maximum 3 indexed parameters per event

## Error Handling

### Require (Pre-condition validation)
```solidity
require(amount > 0, "Amount must be positive");
require(msg.sender == owner, "Only owner");
require(balance >= amount, "Insufficient balance");
```

### Assert (Invariant checking)
```solidity
// Should never fail if code is correct
assert(totalSupply == sumOfAllBalances);
```

### Revert (Explicit rejection)
```solidity
if (amount == 0) {
  revert InvalidAmount();
}

// Custom error (gas efficient, Solidity 0.8.4+)
error InvalidAmount();
```

## Inheritance and Interfaces

### Single Inheritance
```solidity
contract Base {
  uint256 public value;
  function setValue(uint256 _value) public virtual {
    value = _value;
  }
}

contract Derived is Base {
  function setValue(uint256 _value) public override {
    value = _value * 2;
  }
}
```

### Multiple Inheritance
```solidity
contract A { }
contract B { }
contract C is A, B { }
```

### Interfaces
```solidity
interface IERC20 {
  function transfer(address to, uint256 amount) external returns (bool);
  function balanceOf(address account) external view returns (uint256);
}

contract Token is IERC20 {
  // Implement interface functions
}
```

## Access Control

### Ownership Pattern
```solidity
contract Ownable {
  address public owner;

  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }

  function transferOwnership(address newOwner)
    public
    onlyOwner
  {
    owner = newOwner;
  }
}
```

### Role-Based Access Control (RBAC)
```solidity
contract AccessControl {
  mapping(bytes32 => mapping(address => bool)) roles;
  bytes32 public constant ADMIN_ROLE = keccak256("ADMIN");

  modifier onlyRole(bytes32 role) {
    require(roles[role][msg.sender]);
    _;
  }

  function grantRole(bytes32 role, address account)
    public
    onlyRole(DEFAULT_ADMIN_ROLE)
  {
    roles[role][account] = true;
  }
}
```

## External Calls and Interaction

### Calling Other Contracts
```solidity
// Direct call
Token token = Token(tokenAddress);
bool success = token.transfer(recipient, amount);

// Low-level call
(bool success, bytes memory data) = tokenAddress.call(
  abi.encodeWithSignature("transfer(address,uint256)",
    recipient, amount)
);

// Delegatecall (runs target code in caller's context)
(bool success, ) = implementation.delegatecall(
  abi.encodeWithSignature("initialize()")
);
```

### Handling Return Values
```solidity
// Safe transfer pattern
require(token.transfer(recipient, amount), "Transfer failed");

// Or use SafeTransferLib
SafeTransferLib.safeTransfer(token, recipient, amount);
```

## Design Patterns

### Checks-Effects-Interactions
```solidity
function withdraw(uint256 amount) public {
  // 1. Checks
  require(balances[msg.sender] >= amount);

  // 2. Effects (state changes)
  balances[msg.sender] -= amount;

  // 3. Interactions (external calls)
  (bool success, ) = msg.sender.call{value: amount}("");
  require(success);
}
```

### Guard Check Pattern
```solidity
function onlyAfter(uint256 _time) public {
  require(block.timestamp >= _time);
  _;
}

function onlyBefore(uint256 _time) public {
  require(block.timestamp <= _time);
  _;
}
```

### Pulling Over Pushing (Withdrawal Pattern)
```solidity
// Bad: pushing funds
function distribute(address[] memory recipients) public {
  for (uint i = 0; i < recipients.length; i++) {
    recipients[i].call{value: amount}("");  // Can fail
  }
}

// Good: recipients pull funds
function withdraw() public {
  uint256 amount = pendingReturns[msg.sender];
  pendingReturns[msg.sender] = 0;
  (bool success, ) = msg.sender.call{value: amount}("");
  require(success);
}
```

### State Machine Pattern
```solidity
enum State { Created, Locked, Inactive }

modifier inState(State _state) {
  require(state == _state);
  _;
}

function activate() public inState(State.Created) {
  state = State.Locked;
}
```

## Contract Upgrades

### Proxy Pattern (Transparent)
```solidity
// Proxy delegates calls to implementation
proxy.delegatecall(implementation.function);

// Admin can upgrade implementation
function upgradeTo(address newImplementation)
  public
  onlyAdmin
{
  _implementation = newImplementation;
}
```

### Storage Layout
```solidity
// V1
contract StorageV1 {
  address owner;
  uint256 value;
}

// V2 - Append, never reorder
contract StorageV2 {
  address owner;
  uint256 value;
  uint256 newValue;  // New storage slot
}
```

## Libraries

### Using Deployed Libraries
```solidity
library SafeMath {
  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    require(c >= a);
    return c;
  }
}

contract MyContract {
  using SafeMath for uint256;

  uint256 total = a.add(b);
}
```

## Common Pitfalls and Prevention

### Reentrancy
```solidity
// Vulnerable
function withdraw() public {
  uint256 amount = balance[msg.sender];
  (bool success, ) = msg.sender.call{value: amount}("");
  balance[msg.sender] = 0;  // Too late!
}

// Safe
function withdraw() public nonReentrant {
  uint256 amount = balance[msg.sender];
  balance[msg.sender] = 0;  // Before call
  (bool success, ) = msg.sender.call{value: amount}("");
  require(success);
}
```

### Integer Overflow/Underflow
```solidity
// Solidity 0.8.0+ has automatic checks
// Or use SafeMath library for older versions
uint256 x = type(uint256).max;
uint256 y = x + 1;  // Reverts
```

### Timestamp Dependence
```solidity
// Miners can manipulate timestamp slightly
// Don't use for critical randomness
uint256 randomness = block.timestamp;  // Bad

// Use block hash instead (limited to recent blocks)
uint256 nonce = uint256(blockhash(block.number - 1));  // Better
```

---

**Key Takeaways**:
- Smart contracts are immutable programs executed on blockchain
- Solidity is the primary language for Ethereum
- Security patterns and best practices are essential
- Events enable efficient off-chain indexing
- Upgradeable contracts use proxy patterns
- External calls require careful handling
