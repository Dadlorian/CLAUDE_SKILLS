# Consensus Mechanisms Reference

## What is Consensus?

Agreement among distributed nodes that:
1. New blocks are valid
2. Transaction order is correct
3. No double-spending occurred
4. Protocol rules are followed

Without consensus, blockchain is just a database.

## Proof of Work (PoW)

### How It Works
```
1. Miners collect pending transactions
2. Create block with merkle tree
3. Solve computational puzzle: find nonce where keccak256(block) < target
4. First solution broadcasts to network
5. Other nodes verify solution (trivial)
6. Miner receives reward (newly created coins + fees)
7. Difficulty adjusts to maintain consistent block time
```

### Difficulty Adjustment
```
If blocks are too fast: Increase difficulty
If blocks are too slow: Decrease difficulty

Target adjustment every ~2 weeks (Bitcoin)
Target: Make average block time 10 minutes (Bitcoin) or 12 seconds (Ethereum pre-merge)
```

### Security Model: 51% Attack
```
Attacker controls >50% hash power
Can:
  - Rewrite history
  - Double-spend
  - Censor transactions

Cost: Prohibitively expensive
Example: Bitcoin ~$20 billion in hardware for 51% attack
```

### Pros
- Proven security
- Fully decentralized
- No special hardware requirements (early Bitcoin)
- Resistant to sybil attacks

### Cons
- Energy intensive (~100 TWh/year for Bitcoin)
- Hardware arms race (ASICs)
- Centralization through mining pools
- 10-minute block times (Bitcoin)

## Proof of Stake (PoS)

### How It Works
```
1. Validators deposit (stake) cryptocurrency
2. Economic security: Act honestly or lose deposit
3. Validators selected to propose blocks
4. Other validators attest (vote) on validity
5. Rewards for honest participation
6. Penalties (slashing) for dishonesty
```

### Block Proposal
```
Selection: Random, weighted by stake
If honest: Earn reward (1-6% APY typical)
If malicious: Lose some/all stake (slashing)

Slashing amounts:
- Corruption: 1% of stake
- Equivocation: Full stake (up to 32 ETH)
```

### Finality
```
Ethereum 2.0:
- 1 slot: 12 seconds
- 1 epoch: 32 slots = 6.4 minutes
- Finality: 2 epochs = 12.8 minutes

Absolute finality: No reorganization possible
```

### Pros
- Energy efficient (99.95% less than PoW)
- Secure without hardware arms race
- Environmental impact minimal
- Faster finality

### Cons
- "Rich get richer" (stake concentration)
- Requires 32 ETH to validate (centralization)
- Requires slashing for security
- Needs layer beyond L1 for censorship-resistant validation

## Delegated Proof of Stake (DPoS)

### How It Works
```
1. Token holders vote for validators (delegates)
2. Top N validators by votes can validate
3. Rewards distributed to holders + delegates
4. Voters can change vote anytime
5. Low barrier to entry for validators
```

### Example: Polkadot
```
Validators: Selected by vote
Nominators: Back validators with stake
Slashing: Penalties for misbehavior
Voting: Stake-weighted
```

### Pros
- More democratic participation
- Lower hardware requirements
- Token holders have direct influence
- Better validator diversity

### Cons
- Voter apathy (few actually vote)
- Potential for vote buying
- Centralization through large stakeholders
- Still requires stake concentration

## Practical Byzantine Fault Tolerance (PBFT)

### How It Works
```
1. One node is "leader" (proposer)
2. Leader proposes value/block
3. All nodes vote on proposal
4. If 2/3+ agree: Consensus reached
5. If leader misbehaves: Vote to replace leader
```

### Fault Tolerance
```
Can tolerate up to 1/3 Byzantine (malicious) nodes
If 2/3 honest: Always reaches consensus
```

### Rounds of Voting
```
Pre-prepare: Leader proposes block
Prepare: Nodes prepare to commit
Commit: Nodes commit after seeing 2/3 prepares

Finality: Immediate after commit phase
```

### Pros
- Instant finality
- No forks possible
- Proven Byzantine fault tolerance

### Cons
- O(n²) message complexity
- Difficult to scale beyond ~100 nodes
- All validators must be known
- Not suitable for open networks

## Proof of Authority (PoA)

### How It Works
```
1. Pre-approved set of validators
2. Validators take turns proposing blocks
3. Validators are known, have reputation at stake
4. Higher trust model than PoW/PoS
5. Faster block times, lower resource requirements
```

### Variants
- **Authority**: Centralized operator
- **Multi-sig**: Multiple signers required
- **Weighted**: Different validators have different weight

### Pros
- Simple to implement
- Fast blocks
- Energy efficient
- Suitable for private networks

### Cons
- Requires trusting validators
- Centralization
- Not suitable for permissionless systems
- Vulnerability to validator compromise

## Proof of History (PoH)

### Used by: Solana

### How It Works
```
1. Create sequence of events with cryptographic timestamp
2. Hash of previous event is input to next
3. Proves events occurred at specific time
4. Separate from consensus, works with PoS
```

### Process
```
Event 1: Hash(previous_hash + data) = hash1
Event 2: Hash(hash1 + data) = hash2
Event 3: Hash(hash2 + data) = hash3
...

Verifiable timeline, cannot forge history
```

### Pros
- Enables fast finality (Solana targets ~400ms)
- Reduces need for synchronization
- Works with other consensus

### Cons
- Different security model
- Requires careful implementation
- Not proven as long-term as PoW

## Proof of Burn (PoB)

### How It Works
```
1. Users send coins to burn address (unspendable)
2. Burned coins grant right to create blocks
3. More coins burned = more block creation rights
4. Alternative to stake
```

### Use Case
```
Doesn't require pre-existing wealth
Can bootstrap new chains
```

### Cons
```
Wasteful (burns actual value)
Less tested than PoW/PoS
Not widely adopted
```

## Hybrid Approaches

### PoW + PoS Hybrid
```
Block proposal: PoS validators
Security: PoW chain witnesses votes
Combination of both security models
```

### Delegated PoS + BFT
```
DPoS elects validators
BFT consensus among validators
Finality + scalability
Example: Cosmos (Tendermint)
```

## Comparative Analysis

### Decentralization
```
PoW: Highly decentralized (anyone can mine)
PoS: Moderate (stake concentration risk)
DPoS: Moderate (voter concentration)
PoA: Centralized (known validators)
PoH: Depends on implementation
```

### Finality
```
PoW: Probabilistic (6+ blocks = ~1 hour)
PoS: Absolute (2 epochs = ~13 minutes)
PBFT: Absolute (end of commit phase)
PoA: Absolute (next block)
```

### Energy Efficiency
```
PoW: Very high consumption (~100+ TWh/year)
PoS: Minimal consumption (~0.005 TWh/year)
DPoS: Minimal consumption
PoA: Minimal consumption
PoH: Minimal consumption
```

### Security Assumption
```
PoW: Majority honest (computational power)
PoS: Majority honest (stake)
PBFT: 2/3 honest (participants)
PoA: Validators honest (reputation)
PoH: Valid timestamps (clock)
```

## Attacking Consensus

### PoW Attacks
```
51% attack: Require majority hash power
Selfish mining: Keep blocks to gain advantage
Eclipse attack: Isolate node from network
```

### PoS Attacks
```
Nothing at stake: Cost-free attacks
Validator apathy: Not keeping validator online
Censorship: Validators exclude transactions
```

### Mitigations
```
PoW: Difficulty increases over time
PoS: Slashing penalties, finality mechanisms
PoA: Validator replacement, reputation
```

## Future Developments

### Casper (Finality Gadget)
```
Adds finality to PoW chains
Validators put down deposits
Penalties for conflicting finality claims
Used in Ethereum 2.0 (renamed to "consensus")
```

### Long-Range Attacks
```
PoS vulnerability: Rewriting distant history
Mitigated by: Weak subjectivity
New validators check validator set at joining
Cannot rewrite far in past
```

### Validator Centralization
```
Risk: Staking pools concentrate stake
Solution: Incentivize solo staking
          Diversify validator set
          Encourage new entrants
```

---

**Key Takeaways**:
- PoW provides decentralized security at energy cost
- PoS provides efficient security with stake commitment
- Different mechanisms suit different use cases
- Hybrid approaches combine benefits
- Finality, energy, and decentralization involve trade-offs
- Network security depends on consensus mechanism choice
