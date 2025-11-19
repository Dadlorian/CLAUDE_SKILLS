# Blockchain Fundamentals Reference

## Core Concepts

### What is Blockchain?
Blockchain is a distributed ledger technology that maintains a continuously growing list of records called blocks. Each block contains:
- **Cryptographic hash** of the previous block
- **Transaction data** or state changes
- **Timestamp** of creation
- **Nonce** (for PoW) or other consensus data

### Key Properties
1. **Decentralization**: No single point of control
2. **Immutability**: Once recorded, data is extremely difficult to alter
3. **Transparency**: All participants can see transactions (on public blockchains)
4. **Security**: Cryptographic protection of data
5. **Consensus**: Agreement mechanism for new blocks

## Distributed Ledger Technology

### Peer-to-Peer Networks
- Nodes communicate directly without central server
- Message propagation through network
- Network topology: Full nodes, light clients, validators
- Synchronization mechanisms for state consistency

### Block Structure
```
Block {
  hash: keccak256(blockHeader)
  parentHash: previous block's hash
  blockNumber: sequential block number
  timestamp: Unix timestamp
  miner/validator: who created the block
  transactions: array of transactions
  stateRoot: merkle root of state tree
  receiptsRoot: merkle root of transaction receipts
  logsBloom: filter for logs
  gasUsed: total gas consumed
  gasLimit: maximum gas allowed
  difficulty/nonce: consensus data
}
```

### Transaction Structure
```
Transaction {
  nonce: transaction count from sender
  gasPrice: price per unit of gas
  gasLimit: maximum gas for execution
  to: recipient address
  value: amount to transfer
  data: transaction payload (contract bytecode or call data)
  v, r, s: ECDSA signature components
}
```

## Cryptography

### Hashing Functions
- **Keccak-256**: Primary hash function in Ethereum
- **SHA-256**: Bitcoin and other applications
- **Blake2b**: Some modern systems

#### Hash Properties
- **Deterministic**: Same input always produces same output
- **Quick**: Fast computation
- **Avalanche effect**: Small input change produces completely different hash
- **One-way**: Cannot reverse to find original input
- **Collision-resistant**: Virtually impossible to find two inputs with same hash

### Digital Signatures (ECDSA)
- Private key: Secret number known only to owner
- Public key: Derived from private key, can be shared
- Signing: Hash message and encrypt with private key
- Verification: Decrypt signature with public key to verify sender

#### Key Derivation
```
Private Key → Public Key (via elliptic curve multiplication)
Public Key → Address (via hashing and taking last 20 bytes)
```

### Merkle Trees
- Binary tree where each leaf is a transaction hash
- Parent nodes contain hash of concatenated children
- Root hash is stored in block header
- Enables efficient proof of transaction inclusion
- Used for light client verification

## Consensus Mechanisms

### Proof of Work (PoW)
- Miners solve computationally difficult puzzles
- Difficulty adjusts based on hash rate
- First to solve gets to add block and earn reward
- Energy-intensive but highly secure
- Used by: Bitcoin, Ethereum (pre-Merge)

**Process**:
1. Miners collect pending transactions
2. Solve mathematical puzzle (find nonce)
3. First solution propagates to network
4. Other nodes verify and accept block
5. Miner receives block reward + transaction fees

### Proof of Stake (PoS)
- Validators stake cryptocurrency as collateral
- Random validator selection for new blocks
- Slashing for malicious behavior
- Energy-efficient
- Used by: Ethereum (post-Merge), Cardano, Polkadot

**Process**:
1. Validators deposit cryptocurrency
2. Random selection based on stake
3. Validator proposes new block
4. Network attestations validate
5. Rewards for correct validation, penalties for dishonesty

### Practical Byzantine Fault Tolerance (PBFT)
- Consensus through rounds of voting
- Tolerates up to 1/3 malicious nodes
- Finality after predetermined rounds
- Used in Hyperledger Fabric, some PoS implementations

### Other Mechanisms
- **Delegated Proof of Stake (DPoS)**: Token holders vote for validators
- **Proof of Authority (PoA)**: Pre-approved validators
- **Proof of History (PoH)**: Verifiable historical record (Solana)
- **Hybrid**: Combination of multiple mechanisms

## Bitcoin vs Ethereum

### Bitcoin
- **Purpose**: Digital currency
- **Scripting**: Limited, stack-based language
- **State**: UTXO (Unspent Transaction Output) model
- **Consensus**: Proof of Work
- **Finality**: 6+ blocks for practical finality (~1 hour)
- **Block Time**: ~10 minutes

### Ethereum
- **Purpose**: Platform for smart contracts
- **Scripting**: Turing-complete (Solidity)
- **State**: Account model with world state
- **Consensus**: Proof of Stake (post-Merge)
- **Finality**: 2 epochs (12.8 minutes) for consensus finality
- **Block Time**: ~12 seconds

## State Management

### Account Model (Ethereum)
```
Account {
  nonce: transaction count
  balance: ETH balance
  storageRoot: merkle root of storage trie
  codeHash: hash of contract code
}
```

### World State Tree
- Merkle Patricia Trie containing all accounts
- Efficient updates and proofs
- stateRoot in block header commits to state
- Allows light clients to verify account balances

### UTXO Model (Bitcoin)
- Each output is discrete, unspent transaction output
- Transaction consumes inputs and creates new outputs
- No account concept, only unspent outputs
- More privacy-preserving in some aspects

## Smart Contracts

### What are Smart Contracts?
- Self-executing code on blockchain
- Automatically executed when conditions met
- Immutable once deployed
- Run on Ethereum Virtual Machine (EVM)

### Contract Lifecycle
1. **Development**: Write code in Solidity
2. **Compilation**: Compile to bytecode
3. **Deployment**: Send to blockchain via transaction
4. **Execution**: Run on every node in network
5. **State Change**: Update world state
6. **Verification**: Nodes verify execution independently

## Network Layers

### Layer 1 (Base Layer)
- Bitcoin, Ethereum, Cardano
- Handles consensus and final settlement
- Limited throughput due to decentralization trade-offs
- ~15-30 transactions per second for Bitcoin/Ethereum

### Layer 2 Solutions
- Operate on top of Layer 1
- Batch transactions off-chain
- Settle periodically to Layer 1
- Examples: Optimistic Rollups, ZK Rollups, State Channels

### Sidechains
- Independent blockchains with own consensus
- Bridge to main chain
- Examples: Polygon, Arbitrum, Optimism

## Security Considerations

### 51% Attack
- Attacker controls majority hash power
- Can reorganize blockchain history
- Cost prohibitive on large networks
- Less effective with PoS

### Double Spending
- Prevented through consensus mechanism
- Requires controlling majority
- Reason for confirmation requirements

### Sybil Attacks
- Attacker creates many identities
- Mitigated through stake requirements
- Work requirements (PoW)

## Future Evolution

- **Scalability**: Layer 2 solutions, sharding
- **Interoperability**: Cross-chain bridges
- **Privacy**: zk-proofs, Monero-like features
- **Sustainability**: Energy-efficient consensus
- **Regulation**: Compliance frameworks

---

**Key Takeaways**:
- Blockchain provides decentralized, immutable record-keeping
- Consensus mechanisms ensure agreement without central authority
- Cryptography secures data and identities
- Smart contracts enable programmable finance
- Multiple design choices create different trade-offs
