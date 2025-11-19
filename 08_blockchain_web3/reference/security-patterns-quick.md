# Security Patterns Quick Guide

## Must-Have Protections

### 1. Reentrancy Guard
```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contract Safe is ReentrancyGuard {
    function withdraw() external nonReentrant { }
}
```

### 2. Access Control
```solidity
import "@openzeppelin/contracts/access/Ownable.sol";
function criticalFunction() external onlyOwner { }
```

### 3. Pausable
```solidity
import "@openzeppelin/contracts/security/Pausable.sol";
function deposit() external whenNotPaused { }
```

### 4. Pull Over Push
```solidity
// ✅ GOOD: Users pull
mapping(address => uint) public pendingRewards;
function claim() external { }

// ❌ BAD: Contract pushes
function distribute(address[] memory users) { }
```

### 5. Input Validation
```solidity
require(amount > 0, "Zero amount");
require(to != address(0), "Zero address");
require(deadline >= block.timestamp, "Expired");
```

## Quick Checks
- [ ] ReentrancyGuard on payable functions
- [ ] Access control on privileged functions
- [ ] Input validation on all external functions
- [ ] SafeERC20 for token transfers
- [ ] Slippage protection on swaps
- [ ] Oracle staleness checks
