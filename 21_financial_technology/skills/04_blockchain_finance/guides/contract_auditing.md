# Contract Auditing Guide

## Self-Audit Checklist

### Access Control
- [ ] All sensitive functions have access control
- [ ] Owner functions use Ownable or AccessControl
- [ ] Roles properly separated (onlyOwner, onlyMinter, etc.)
- [ ] No accidental public functions

### State Management
- [ ] No uninitialized state variables
- [ ] Proper validation of user inputs
- [ ] State changes before external calls (CEI)
- [ ] No double-spends or replay attacks
- [ ] Invariants maintained across operations

### Reentrancy Protection
- [ ] ReentrancyGuard used for external calls
- [ ] Checks-effects-interactions pattern followed
- [ ] No direct ETH transfers (use call)
- [ ] Low-level calls carefully handled

### Integer Operations
- [ ] No overflow/underflow (Solidity 0.8+ or SafeMath)
- [ ] Division before multiplication (avoid loss of precision)
- [ ] Proper rounding handled
- [ ] Boundary conditions tested

### Token Operations
- [ ] Safe transfer patterns used
- [ ] Return values checked
- [ ] Approval mechanisms properly handled
- [ ] Fee-on-transfer tokens considered

### Oracles
- [ ] Multiple oracle sources used
- [ ] Price staleness checked
- [ ] TWAP instead of spot price
- [ ] Oracle failure handling

### Emergency Mechanisms
- [ ] Pause/emergency stop implemented
- [ ] Circuit breakers for extreme values
- [ ] Recovery mechanisms exist
- [ ] Time locks for sensitive changes

## Static Analysis Tools

### Slither
```bash
# Install
pip install slither-analyzer

# Run analysis
slither contract.sol

# Check specific issues
slither contract.sol --detect reentrancy,uninitialized-state-variables
```

### Mythril
```bash
# Install
pip install mythril

# Analyze contract
myth analyze contract.sol

# Check for specific vulnerabilities
myth analyze --onchain-provider http://localhost:8545 0x...
```

### Solhint
```bash
# Install
npm install solhint

# Run linter
solhint contracts/**/*.sol

# Check specific rules
solhint --rules external-calls-first contracts/
```

## Manual Code Review Process

### Step 1: Understand Intent
```
1. Read specification
2. Understand use cases
3. Map user flows
4. Identify critical functions
5. Note assumptions
```

### Step 2: Review Core Logic
```
1. Check business logic correctness
2. Verify calculations
3. Test edge cases in mind
4. Identify potential exploits
5. Note deviations from specs
```

### Step 3: Security Review
```
1. Access control verification
2. Input validation
3. Arithmetic correctness
4. External call safety
5. State consistency
```

### Step 4: Gas and Optimization
```
1. Identify expensive operations
2. Suggest gas improvements
3. Check loop bounds
4. Verify efficient storage
5. Consider scalability
```

## Common Vulnerabilities Checklist

### Critical
- [ ] Reentrancy
- [ ] Unchecked external calls
- [ ] Unvalidated input
- [ ] Integer overflow/underflow
- [ ] Access control bypass

### High
- [ ] Timestamp dependence
- [ ] Oracle manipulation
- [ ] Front-running vulnerabilities
- [ ] Flash loan attacks
- [ ] Unhandled exceptions

### Medium
- [ ] Gas limit DoS
- [ ] Inefficient loops
- [ ] Redundant operations
- [ ] Poor error handling
- [ ] Lack of events

### Low
- [ ] Code style
- [ ] Documentation
- [ ] Gas optimization
- [ ] Code clarity
- [ ] Test coverage

## Professional Audit Preparation

### Before Submitting to Auditor

```
1. Code Cleanliness
   - Remove debug code
   - Fix linter warnings
   - Add comments
   - Follow style guide

2. Documentation
   - Write specification
   - Document assumptions
   - Explain complex logic
   - Provide architecture diagram

3. Testing
   - Unit tests pass
   - Integration tests pass
   - Coverage > 90%
   - Gas tests completed

4. Deployment Readiness
   - Testnet deployment successful
   - Contract verification planned
   - Emergency procedures ready
   - Monitoring setup planned
```

### What to Expect from Auditor

```
1. Automated Analysis
   - Static analysis tools
   - Gas analysis
   - Pattern matching

2. Manual Review
   - Expert code review
   - Architecture analysis
   - Design pattern verification

3. Testing
   - Functional testing
   - Edge case testing
   - Exploit attempts
   - Fuzzing (if applicable)

4. Report
   - Issues categorized by severity
   - Detailed descriptions
   - Proof of concepts
   - Recommendations
```

## Vulnerability Examples and Fixes

### Example 1: Unvalidated Input
```solidity
// Bad
function withdraw(uint256 amount) public {
    balances[msg.sender] -= amount;
    msg.sender.call{value: amount}("");
}

// Good
function withdraw(uint256 amount) public nonReentrant {
    require(amount > 0, "Amount must be positive");
    require(balances[msg.sender] >= amount, "Insufficient balance");

    balances[msg.sender] -= amount;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

### Example 2: Missing Access Control
```solidity
// Bad
function mint(address to, uint256 amount) public {
    totalSupply += amount;
    balances[to] += amount;
}

// Good
function mint(address to, uint256 amount) public onlyOwner {
    totalSupply += amount;
    balances[to] += amount;
    emit Transfer(address(0), to, amount);
}
```

### Example 3: Reentrancy
```solidity
// Bad
function withdraw(uint256 amount) public {
    uint256 balance = balances[msg.sender];
    require(balance >= amount);

    msg.sender.call{value: amount}("");  // Reentrancy here!
    balances[msg.sender] = 0;
}

// Good
function withdraw(uint256 amount) public nonReentrant {
    uint256 balance = balances[msg.sender];
    require(balance >= amount);

    balances[msg.sender] = 0;             // Effect first
    (bool success, ) = msg.sender.call{value: amount}("");  // Interaction last
    require(success);
}
```

## Monitoring After Deployment

### On-Chain Monitoring
```javascript
// Monitor unusual activity
const filter = contract.filters.Transfer();

contract.on(filter, (from, to, value, event) => {
  if (value > threshold) {
    alert(`Large transfer detected: ${ethers.formatEther(value)} ETH`);
  }
});

// Monitor failed transactions
provider.on("error", (error) => {
  console.error("Network error:", error);
});
```

### Metrics to Track
```
1. Transaction volume
2. Failed transactions
3. Gas prices
4. Balance anomalies
5. Function call patterns
6. Error event emissions
```

---

**Key Takeaways**:
- Use automated tools first
- Follow manual review checklist
- Common vulnerabilities to watch for
- Professional audits recommended
- Monitoring critical post-deployment
