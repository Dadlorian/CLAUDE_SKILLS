# Smart Contract Security Audit Checklist

Comprehensive checklist for auditing smart contracts before production deployment.

## Pre-Audit Preparation

### Documentation Review
- [ ] **Whitepaper/Technical Spec**: Understand intended functionality
- [ ] **Architecture Diagrams**: Review system design and data flows
- [ ] **Known Issues**: Review any documented concerns
- [ ] **Previous Audits**: Check for repeat issues
- [ ] **Test Coverage**: Verify >95% line and branch coverage
- [ ] **NatSpec Comments**: All functions documented

### Scope Definition
- [ ] **Contract List**: All contracts in scope identified
- [ ] **External Dependencies**: Third-party contracts/libraries listed
- [ ] **Deployment Environment**: Target chain(s) specified
- [ ] **Privileged Roles**: Admin/owner capabilities documented
- [ ] **Upgrade Mechanism**: Upgradeability strategy clear

## Critical Security Issues (CRITICAL)

### Access Control
- [ ] **Ownership Verification**: Only legitimate addresses can call privileged functions
- [ ] **Role Management**: Proper role-based access control (RBAC)
- [ ] **Multi-sig Required**: Critical operations require multi-signature
- [ ] **Timelock Protection**: Admin changes have time delays
- [ ] **Frontrunning Protection**: Admin can't frontrun users
- [ ] **Centralization Risks**: Single points of failure identified
- [ ] **Emergency Pause**: Circuit breaker mechanism exists
- [ ] **Role Renunciation**: Can renounce ownership if needed

```solidity
// ❌ BAD: No access control
function withdraw() external {
    payable(msg.sender).transfer(address(this).balance);
}

// ✅ GOOD: Proper access control
function withdraw() external onlyOwner {
    payable(owner()).transfer(address(this).balance);
}
```

### Reentrancy
- [ ] **Checks-Effects-Interactions**: Pattern followed everywhere
- [ ] **ReentrancyGuard**: Used on all state-changing external calls
- [ ] **Read-Only Reentrancy**: Protected against view function reentrancy
- [ ] **Cross-Function Reentrancy**: Multiple functions checked
- [ ] **ERC-777 Tokens**: Callback reentrancy considered
- [ ] **External Calls**: All external calls after state changes

```solidity
// ❌ BAD: Reentrancy vulnerability
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] -= amount; // State change AFTER external call
}

// ✅ GOOD: Checks-Effects-Interactions
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount); // Checks
    balances[msg.sender] -= amount; // Effects
    (bool success, ) = msg.sender.call{value: amount}(""); // Interactions
    require(success);
}
```

### Integer Overflow/Underflow
- [ ] **Solidity Version**: Using 0.8.0+ with built-in checks
- [ ] **Unchecked Blocks**: Only used where provably safe
- [ ] **Type Conversions**: Safe casting (no truncation)
- [ ] **Multiplication Before Division**: Order of operations safe
- [ ] **SafeMath (if <0.8)**: Used for all arithmetic

### Oracle Manipulation
- [ ] **Price Oracle Security**: Using TWAP or multiple sources
- [ ] **Chainlink Integration**: Proper staleness checks
- [ ] **Fallback Oracles**: Backup price sources
- [ ] **Price Bounds**: Sanity checks on oracle data
- [ ] **Oracle Update Frequency**: Adequate for use case
- [ ] **Flash Loan Resistance**: Price can't be manipulated in single tx

```solidity
// ✅ GOOD: Chainlink with staleness check
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
```

### Flash Loan Attacks
- [ ] **Flash Loan Protection**: Price/state can't be manipulated in single tx
- [ ] **TWAP Usage**: Time-weighted average prices used
- [ ] **Block-based Limits**: Rate limiting based on blocks
- [ ] **State Snapshots**: Critical values snapshot at tx start
- [ ] **Invariant Checks**: Core invariants verified post-operation

## High Severity Issues (HIGH)

### Economic Security
- [ ] **Slippage Protection**: User-defined slippage limits enforced
- [ ] **Price Impact**: Large trades don't break protocol
- [ ] **Fee Calculation**: Fees calculated correctly, no rounding exploits
- [ ] **Reward Distribution**: Fair and accurate reward calculations
- [ ] **Liquidity Draining**: Can't drain liquidity through exploits
- [ ] **Interest Rate Models**: Rates calculated correctly
- [ ] **Collateral Factors**: Proper liquidation thresholds

### Token Handling
- [ ] **Transfer Return Values**: Check return values (or use SafeERC20)
- [ ] **Fee-on-Transfer Tokens**: Handled correctly
- [ ] **Rebasing Tokens**: Balance changes handled
- [ ] **ERC-777 Hooks**: Callback vulnerabilities considered
- [ ] **Approval Race Condition**: Using increaseAllowance/decreaseAllowance
- [ ] **Token Decimals**: Handled correctly (not assumed to be 18)

```solidity
// ❌ BAD: Not checking return value
token.transfer(recipient, amount);

// ✅ GOOD: Using SafeERC20
token.safeTransfer(recipient, amount);
```

### Logic Errors
- [ ] **Initialization**: Contract properly initialized (no double init)
- [ ] **State Transitions**: All state transitions valid
- [ ] **Edge Cases**: Boundary conditions tested
- [ ] **Zero Values**: Handling of zero addresses/amounts
- [ ] **Arithmetic**: All calculations correct and safe
- [ ] **Loop Bounds**: No off-by-one errors

### Front-Running/MEV
- [ ] **Transaction Ordering**: MEV opportunities minimized
- [ ] **Commit-Reveal**: Used for sensitive operations
- [ ] **Batch Processing**: Transactions batched where possible
- [ ] **Fair Ordering**: First-come-first-served when appropriate
- [ ] **Deadline Parameters**: All time-sensitive functions have deadlines

## Medium Severity Issues (MEDIUM)

### Gas Optimization & DoS
- [ ] **Unbounded Loops**: No loops over unbounded arrays
- [ ] **Gas Limits**: Operations won't hit block gas limit
- [ ] **Griefing Attacks**: Can't force others to spend excess gas
- [ ] **Block Stuffing**: Protocol works under congestion
- [ ] **Storage Efficient**: Gas-optimized storage patterns

```solidity
// ❌ BAD: Unbounded loop
function distributeRewards(address[] memory users) external {
    for (uint i = 0; i < users.length; i++) {
        // Could run out of gas
        _transfer(users[i], calculateReward(users[i]));
    }
}

// ✅ GOOD: Bounded operations
function claimReward() external {
    uint256 reward = calculateReward(msg.sender);
    _transfer(msg.sender, reward);
}
```

### Timestamp Dependence
- [ ] **Block Timestamp**: Not used for critical randomness
- [ ] **Time Manipulation**: 15-second tolerance acceptable
- [ ] **Deadline Checks**: Using block.timestamp appropriately
- [ ] **Time-based Logic**: Not exploitable by miners

### Randomness
- [ ] **No Predictable RNG**: Not using blockhash/timestamp for randomness
- [ ] **VRF Integration**: Chainlink VRF or similar for true randomness
- [ ] **Commit-Reveal**: Used when VRF not available
- [ ] **Entropy Sources**: Multiple sources combined

### Upgradeability
- [ ] **Storage Collisions**: No storage slot conflicts
- [ ] **Initialization**: Initializers protected from re-initialization
- [ ] **Upgrade Authorization**: Only authorized addresses can upgrade
- [ ] **Storage Layout**: Gaps included for future storage
- [ ] **Upgrade Testing**: Upgrade path tested on fork

```solidity
// ✅ GOOD: Storage gaps for upgradeability
contract MyContract {
    uint256 public value1;
    uint256 public value2;

    // Reserve 50 storage slots for future use
    uint256[50] private __gap;
}
```

## Low Severity Issues (LOW)

### Code Quality
- [ ] **Compiler Version**: Latest stable version used
- [ ] **Compiler Warnings**: No warnings during compilation
- [ ] **Dead Code**: No unused functions/variables
- [ ] **TODO Comments**: All TODOs resolved
- [ ] **Magic Numbers**: Constants used instead of literals
- [ ] **Naming Conventions**: Consistent and clear naming

### Events & Logging
- [ ] **State Changes**: All state changes emit events
- [ ] **Indexed Parameters**: Key parameters indexed for filtering
- [ ] **Event Completeness**: Events contain all relevant data
- [ ] **No Missing Events**: Critical operations log events

### Error Handling
- [ ] **Custom Errors**: Using custom errors (gas efficient)
- [ ] **Descriptive Messages**: Error messages are clear
- [ ] **Revert Conditions**: All failure modes handled
- [ ] **Error Propagation**: Errors from external calls handled

### Function Visibility
- [ ] **Minimal Visibility**: Functions have minimal required visibility
- [ ] **External vs Public**: Using external when possible
- [ ] **Private/Internal**: Internal functions marked appropriately
- [ ] **State Mutability**: view/pure marked correctly

## Informational Issues

### Documentation
- [ ] **NatSpec Complete**: All public functions documented
- [ ] **Parameter Descriptions**: All parameters explained
- [ ] **Return Values**: Return values documented
- [ ] **Invariants**: Protocol invariants documented
- [ ] **Assumptions**: All assumptions stated

### Best Practices
- [ ] **OpenZeppelin**: Using battle-tested libraries
- [ ] **EIP Compliance**: Following relevant EIPs
- [ ] **Gas Patterns**: Following gas optimization patterns
- [ ] **Security Patterns**: Following security best practices

## DeFi-Specific Checks

### AMM/DEX
- [ ] **K Invariant**: Constant product maintained
- [ ] **Minimum Liquidity**: Locked on first deposit
- [ ] **Price Oracle Updates**: TWAP updated correctly
- [ ] **Fee Calculation**: Fees calculated and distributed correctly
- [ ] **Slippage Protection**: Users protected from excessive slippage
- [ ] **Flash Swap Protection**: Can't exploit flash swaps

### Lending Protocol
- [ ] **Interest Accrual**: Interest calculated correctly
- [ ] **Collateralization**: Over-collateralization enforced
- [ ] **Liquidation Logic**: Liquidations fair and profitable
- [ ] **Health Factor**: Calculated correctly
- [ ] **Utilization Rate**: Interest rate model correct
- [ ] **Bad Debt**: Handled appropriately

### Staking
- [ ] **Reward Calculation**: Rewards distributed fairly
- [ ] **Staking/Unstaking**: Proper accounting
- [ ] **Reward Inflation**: Controlled and predictable
- [ ] **Early Withdrawal**: Penalties calculated correctly
- [ ] **Compounding**: Auto-compound logic correct

### Governance
- [ ] **Voting Power**: Calculated correctly
- [ ] **Quorum**: Minimum participation enforced
- [ ] **Proposal Execution**: Only approved proposals execute
- [ ] **Timelock**: Critical changes have time delays
- [ ] **Vote Delegation**: Delegation works correctly
- [ ] **Snapshot Blocks**: Vote power at specific block

## NFT-Specific Checks

### Minting
- [ ] **Supply Cap**: Max supply enforced
- [ ] **Mint Price**: Price calculation correct
- [ ] **Allowlist**: Merkle proof validation correct
- [ ] **Reentrancy**: Protected on mint
- [ ] **Refunds**: Excess ETH refunded

### Metadata
- [ ] **Token URI**: Returns correct URI
- [ ] **Reveal Mechanism**: Works as intended
- [ ] **Metadata Immutability**: Can't be changed maliciously
- [ ] **IPFS Pinning**: Metadata permanently available

### Royalties
- [ ] **ERC-2981**: Properly implemented
- [ ] **Royalty Calculation**: Percentages correct
- [ ] **Receiver Address**: Can be updated if needed

## Testing Requirements

### Unit Tests
- [ ] **Coverage >95%**: Line and branch coverage
- [ ] **Edge Cases**: All edge cases tested
- [ ] **Fuzz Testing**: Randomized input testing
- [ ] **Invariant Tests**: Protocol invariants tested

### Integration Tests
- [ ] **Multi-Contract**: Interactions tested
- [ ] **External Protocols**: Third-party integrations tested
- [ ] **Upgrade Paths**: Upgrades tested

### Fork Tests
- [ ] **Mainnet Fork**: Tested against real state
- [ ] **Protocol Integrations**: Real protocol interactions tested
- [ ] **Attack Scenarios**: Known attacks tested

## Automated Tool Analysis

### Slither
- [ ] **No High/Critical**: All critical findings resolved
- [ ] **Medium Reviewed**: Medium findings reviewed and addressed
- [ ] **Detectors**: All relevant detectors run

### Mythril
- [ ] **Symbolic Execution**: No critical vulnerabilities
- [ ] **Known Patterns**: No known vulnerability patterns

### Echidna
- [ ] **Invariant Testing**: All invariants hold
- [ ] **Property Tests**: Properties verified

### Certora (Formal Verification)
- [ ] **Specifications**: Key properties formally verified
- [ ] **Prover**: All specs proven correct

## Deployment Checklist

### Pre-Deployment
- [ ] **Constructor Args**: Verified correct
- [ ] **Initial State**: Correct initial configuration
- [ ] **Gas Limits**: Deployment won't fail
- [ ] **Network**: Deploying to correct network

### Post-Deployment
- [ ] **Verification**: Contracts verified on Etherscan
- [ ] **Ownership Transfer**: To multi-sig or governance
- [ ] **Timelock Setup**: For critical operations
- [ ] **Pause Mechanism**: Emergency pause available
- [ ] **Monitoring**: Events and transactions monitored

## Final Sign-Off

### Critical Confirmations
- [ ] **No Critical Issues**: All critical issues resolved
- [ ] **High Issues Mitigated**: High severity issues addressed
- [ ] **Test Coverage**: >95% coverage achieved
- [ ] **External Audit**: Professional audit completed
- [ ] **Bug Bounty**: Program launched
- [ ] **Insurance**: Protocol insurance considered
- [ ] **Incident Response**: Plan in place
- [ ] **Documentation**: User and developer docs complete

### Recommended Actions
- [ ] **Gradual Rollout**: Start with limited funds/users
- [ ] **Monitoring Dashboard**: Real-time monitoring active
- [ ] **Emergency Contacts**: Multi-sig signers ready
- [ ] **Community Communication**: Users informed of risks
- [ ] **Upgrade Plan**: Clear upgrade path if issues found

---

## Severity Definitions

**CRITICAL**: Immediate loss of funds, protocol insolvency, unauthorized access
**HIGH**: Potential loss of funds, protocol manipulation, DoS
**MEDIUM**: Indirect loss, griefing, gas inefficiency
**LOW**: Code quality, best practices, informational

---

## Tools Reference

- **Slither**: `slither .`
- **Mythril**: `myth analyze contracts/MyContract.sol`
- **Echidna**: `echidna-test . --contract MyContract --config echidna.yaml`
- **Foundry**: `forge test --gas-report`
- **Hardhat**: `npx hardhat test --gas-reporter`
- **Coverage**: `forge coverage` or `npx hardhat coverage`

---

**Remember**: Security is not a one-time check. Continuous monitoring and updates are essential for production protocols.
