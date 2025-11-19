# MEV Protection Strategies

## MEV Types
1. **Front-running**: Bot sees tx, submits higher gas
2. **Back-running**: Bot submits tx right after target
3. **Sandwich attacks**: Front-run + back-run
4. **Liquidation sniping**: Bot liquidates before others

## Protection Strategies

### 1. Slippage Protection
```solidity
function swap(uint amountIn, uint minAmountOut) external {
    uint amountOut = calculateOutput(amountIn);
    require(amountOut >= minAmountOut, "Slippage exceeded");
}
```

### 2. Commit-Reveal
```solidity
function commit(bytes32 hash) external {
    commits[msg.sender] = hash;
}

function reveal(uint amount, bytes32 secret) external {
    require(keccak256(abi.encodePacked(amount, secret)) == commits[msg.sender]);
    // Execute with amount
}
```

### 3. Batch Auctions
Group transactions, execute at same price.

### 4. Flashbots
Submit transactions privately to avoid mempool.

### 5. Time Locks
```solidity
mapping(address => uint) public actionTimestamps;

function action() external {
    require(block.timestamp > actionTimestamps[msg.sender] + 1 minutes);
    actionTimestamps[msg.sender] = block.timestamp;
}
```

### 6. Fair Sequencing
Use Chainlink FSS or similar for order fairness.

## MEV Mitigation Checklist
- [ ] Slippage limits on all swaps
- [ ] Deadline parameters
- [ ] Commit-reveal for sensitive ops
- [ ] Consider Flashbots
- [ ] Monitor for sandwich attacks
- [ ] Use private RPCs when needed
