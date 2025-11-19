# Layer 2 Solutions Reference

## Why Layer 2?

### Ethereum Mainnet Limitations
```
- Throughput: ~15 TPS
- Latency: 12-second blocks
- Cost: $0.50-$100+ per transaction
- Scalability: Limited by consensus

Need: 1000x+ improvement for mass adoption
```

### Layer 2 Approach
```
- Execute off-chain
- Settle periodically to mainnet
- Inherit Ethereum security
- 100-4000x throughput increase
```

## Rollups Overview

### Core Principle
```
Bundle multiple transactions off-chain
Compress into single proof
Settle on mainnet
Verify proof on-chain

State: [tx1, tx2, tx3, tx4] → [proof] → mainnet
```

### Cost Breakdown
```
Optimistic Rollup: ~$0.01-0.10 per tx
ZK Rollup: ~$0.01-0.05 per tx
Mainnet: ~$0.50-$100+ per tx
```

## Optimistic Rollups

### Mechanism
```
1. Operator collects transactions
2. Batch and compress off-chain
3. Submit to mainnet (optimistic = assume valid)
4. Challenge period (7 days): Anyone can dispute
5. If disputed: Execute transaction on mainnet to verify
6. Operator loses bond if wrong, gets reward if right
```

### Challenge Process
```
State commitment: [batch 1] [batch 2] [batch 3]
                     ↓
Any user can challenge batch 2
Mainnet executes to verify
If operator wrong: batch invalid, user gets bond
If operator right: challenger pays penalty
```

### Pros
- Simple to understand
- Minimal cryptographic assumptions
- EVM-compatible (can run existing code)
- Proven security model

### Cons
- Long withdrawal times (7 days dispute period)
- Higher storage requirements
- Operator can censor transactions (mitigated)

### Examples
- **Optimism**: EVM-equivalent
- **Arbitrum**: EVM-compatible
- **Base**: Built on OP Stack
- **Metis**: Multi-VM support

## ZK (Zero-Knowledge) Rollups

### Mechanism
```
1. Operator collects transactions
2. Execute off-chain
3. Generate zero-knowledge proof
4. Submit proof to mainnet
5. Mainnet verifies proof (mathematical proof of correctness)
6. No challenge period needed
```

### Proof Process
```
Prover: "I executed these transactions correctly"
Proof: Mathematical proof (doesn't reveal transactions)
Verifier: Checks proof is valid (very fast)
Result: Instant finality
```

### Zero-Knowledge Property
```
Verifier learns: Transactions were valid
Verifier learns NOT: Transaction details (if using privacy)
Proof size: Constant (small, ~256 bytes)
```

### Pros
- Instant finality (no challenge period)
- Lower storage requirements
- Smaller proof size
- More efficient scaling

### Cons
- Requires new cryptography
- Longer computation for proofs
- May sacrifice EVM compatibility
- More complex to implement

### Examples
- **StarkNet**: STARK proofs
- **zkSync**: PLONK-based proofs
- **Polygon zkEVM**: EVM-equivalent
- **Scroll**: EVM-equivalent rollup

## State Channels

### Mechanism
```
1. Two parties lock funds on mainnet
2. Exchange transactions off-chain
3. Update state locally (instant, free)
4. Only settle final state on mainnet
5. Either party can trigger settlement
```

### Example: Payment Channel
```
Alice deposits 10 ETH → Bob
Alice → Bob: 1 ETH (signed)
Alice → Bob: 0.5 ETH more (cumulative 1.5)
Bob → Alice: 0.1 ETH back (cumulative 1.4)
Final settlement: Alice 8.6 ETH, Bob 11.4 ETH
```

### Pros
- Instant transactions
- Minimal on-chain footprint
- Very cheap operation

### Cons
- Both parties must participate
- Requires keeping channels open
- Limited to 2-party interactions
- Liquidity fragmentation

### Examples
- **Lightning Network**: Bitcoin payments
- **Raiden Network**: Ethereum ERC20 transfers
- **Perun**: Generalized state channels

## Sidechains

### Mechanism
```
Main chain: Ethereum
Side chain: Independent blockchain
Bridge: Lock tokens on main, mint on side
        Lock tokens on side, unmint on main
```

### Characteristics
```
- Own consensus mechanism
- Independent security model
- Can have different rules
- Periodic settlement to main chain
```

### Pros
- Greater flexibility
- Can optimize for specific use case
- Independent upgrades

### Cons
- Separate security guarantees
- Requires bridge trust assumptions
- Not as capital efficient

### Examples
- **Polygon (formerly Matic)**: PoS sidechain
- **Gnosis Chain**: xDai sidechain
- **Skale**: Elastic sidechain network

## Validium vs Volition

### Validium
```
- ZK proofs for computation
- Off-chain data storage
- Requires operator trust for data availability
- Very low cost but less decentralized
```

### Volition
```
- ZK proofs for computation
- Choose per transaction: on-chain vs off-chain data
- Higher flexibility
- Mixed cost/security trade-off
```

## Plasma

### Mechanism
```
Main chain: Stores merkle root only
Plasma chain: Separate blockchain
Exit game: If operator misbehaves, users prove ownership

Challenge period for exit
Reduces data availability requirements
```

### Limitations
```
- Complex exit mechanisms
- Data availability risks
- Largely superseded by Rollups
```

## Cross-Layer Communication

### Mainnet → L2 (Deposit)
```
1. User initiates transaction on mainnet
2. Sends funds/message to L2 bridge
3. L2 detects deposit
4. Funds appear on L2
Typical delay: 10 minutes - 1 hour
```

### L2 → Mainnet (Withdrawal)
```
Optimistic Rollup:
1. User initiates withdrawal on L2
2. Waits 7 days
3. Finalizes on mainnet
Typical delay: 7 days

ZK Rollup:
1. User initiates withdrawal on L2
2. Waits for next batch proof
3. Can withdraw immediately after
Typical delay: Minutes to hours
```

### Message Passing
```
// Optimism
L1CrossDomainMessenger: Send messages L1→L2→L1

// Arbitrum
Inbox/Outbox: Queue messages between layers

// zkSync
L1→L2 Messenger: Similar pattern
```

## Financial Mechanics

### MEV (Maximal Extractable Value)

#### On Mainnet
```
Validators/miners can see pending transactions
Reorder to extract value (front-running)
Sandwich attacks possible
```

#### On L2
```
Operator controls transaction ordering
Can still extract MEV
But: Operator is known, can be regulated
Some L2s: Use PBS (proposer-builder separation)
```

### Gas Costs

#### Optimistic Rollup
```
Calldata: Compressed transaction data
Cost: ~16 gas per zero byte, 4 gas per non-zero byte
Calldata: 80% of L2 transaction cost
Compute: 20% of L2 transaction cost
```

#### ZK Rollup
```
Proof verification: More compute-intensive
Smaller batches possible
Cost: Often lower than Optimistic
```

## Application Considerations

### Mainnet Use Cases
```
- Settlement (final, trustless)
- Collateral deposits
- Long-term positions
- High-value transactions
```

### L2 Use Cases
```
- Trading and swaps
- User interactions
- Low-value payments
- Frequent transactions
```

### Multi-Layer Strategy
```
User deposits on mainnet (trustless)
Operates on L2 (fast, cheap)
Periodically withdraws (cheaper in batch)
```

## Future Developments

### EIP-4844: Proto-Danksharding
```
- Temporary blob data for rollups
- Reduces calldata cost 16x
- Not as permanent as calldata
- Expires after ~18 days
Massive scaling improvement
```

### Full Danksharding
```
- Dedicated data availability layer
- 64 data shards
- Each shard: Scalable bandwidth
- Major protocol upgrade
```

### L3 Solutions
```
L2 chains can also have rollups
Stack multiple layers
Each adds more scaling
Complexity: Protocol fragmentation
```

## Bridge Security

### Bridge Risks
```
- Smart contract bugs
- Validator set attacks
- Oracle manipulation
- Flash loan exploits
```

### Recommendation
```
Use established bridges:
- Official bridges (Optimism, Arbitrum, zkSync)
- Battle-tested (Across, Stargate)
Avoid new/unaudited bridges
Start with small amounts
```

## Comparison Table

| Feature | Optimistic | ZK Rollup | Plasma | Channel | Sidechain |
|---------|-----------|----------|--------|---------|-----------|
| Finality | 7 days* | Minutes | Days | Instant | Hours |
| Throughput | 1000+ TPS | 4000+ TPS | 1000+ TPS | Unlimited | 1000+ TPS |
| EVM Compatible | Yes** | Partial | Yes | Limited | Yes |
| Complexity | Low | High | Medium | High | Medium |
| Security | Ethereum | Ethereum | Validator set | Participants | Validator set |
| Cost | $0.01-0.10 | $0.01-0.05 | $0.001-0.01 | Free | $0.01-1 |

*Can be faster with preconfirmations
**EVM-equivalent or compatible

---

**Key Takeaways**:
- Rollups batch transactions and settle on mainnet
- Optimistic rollups assume validity, ZK proofs verify
- Different trade-offs in finality, complexity, cost
- Layer 2 integration is necessary for Ethereum adoption
- Choose L2 based on use case requirements
