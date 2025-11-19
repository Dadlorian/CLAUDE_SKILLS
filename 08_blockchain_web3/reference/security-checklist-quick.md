# Smart Contract Security Quick Checklist

## Before Deployment

### Critical (Must Fix)
- [ ] No reentrancy vulnerabilities
- [ ] Access control on all privileged functions
- [ ] Using Solidity 0.8+ for overflow protection
- [ ] All external calls checked
- [ ] Input validation on all public/external functions
- [ ] Using SafeERC20 for token transfers
- [ ] No delegatecall to untrusted addresses

### High Priority
- [ ] Slippage protection on swaps
- [ ] Oracle staleness checks
- [ ] Flash loan attack protection
- [ ] Pull over push payment pattern
- [ ] Emergency pause mechanism
- [ ] Timelock on critical admin functions
- [ ] Multi-sig for admin operations

### Testing
- [ ] >95% test coverage
- [ ] All tests passing
- [ ] Fuzz tests for critical functions
- [ ] Fork tests against mainnet
- [ ] Gas benchmarks acceptable
- [ ] Slither analysis clean
- [ ] External audit completed

### Deployment
- [ ] Contracts verified on Etherscan
- [ ] Ownership transferred to multi-sig
- [ ] Initial parameters correct
- [ ] Monitoring/alerts configured
- [ ] Bug bounty program ready
- [ ] Incident response plan documented

## Quick Security Patterns

```solidity
// ✅ Always use these patterns
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract Secure is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;

    function withdraw() external nonReentrant whenNotPaused {
        uint amount = balances[msg.sender];
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}
```
