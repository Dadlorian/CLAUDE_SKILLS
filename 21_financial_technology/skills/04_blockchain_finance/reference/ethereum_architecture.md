# Ethereum Architecture Reference

## Ethereum Protocol Overview

### What is Ethereum?
Ethereum is a decentralized computing platform that enables smart contracts - self-executing programs stored on the blockchain. It evolved from a pure payment system to a full computation platform.

### Core Architecture
```
┌─────────────────────────────────────┐
│      Smart Contracts Layer          │
│  (Solidity, Vyper, etc.)            │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Application Layer                  │
│  (DeFi, NFTs, DAOs, etc.)           │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Ethereum Protocol Layer            │
│  (State machine, consensus)         │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  P2P Network Layer                  │
│  (Gossip protocol, node discovery)  │
└─────────────────────────────────────┘
```

## Ethereum Virtual Machine (EVM)

### EVM Fundamentals
- Stack-based machine with 256-bit words
- 32KB volatile memory
- Persistent storage (state)
- Executes bytecode independently on every node
- Gas system incentivizes efficient code

### Memory Model
1. **Stack**: Max 1024 elements, 256-bit words
2. **Memory**: Volatile, temporary storage during execution
3. **Storage**: Persistent state trie, survives contract calls
4. **Calldata**: Input parameters to function, immutable

### Opcodes
- ~140 opcodes total
- Arithmetic: ADD, SUB, MUL, DIV
- Logic: LT, GT, EQ, AND, OR, NOT
- Hashing: KECCAK256
- Cryptography: ECRECOVER, SIGNEXTEND
- Storage: SSTORE, SLOAD
- Control: JUMP, JUMPI, PC, STOP
- Memory: MLOAD, MSTORE

### Execution Flow
```
1. Transaction sent to network
2. Included in mempool
3. Node receives transaction
4. Validate signature and nonce
5. Execute transaction with EVM
6. If contract call:
   - Load code from storage
   - Execute bytecode
   - Update state (SSTORE operations)
   - Record logs (events)
7. Calculate gas consumed
8. Update account balances
9. Include in block
10. Broadcast block to network
11. Other nodes verify independently
```

## Account Model

### Externally Owned Accounts (EOAs)
- Controlled by private keys
- Can initiate transactions
- No code associated
- Balance of ETH

### Contract Accounts
- Deployed via transaction
- Code stored on blockchain
- Persistent storage
- Can be triggered by transactions or other contracts
- No balance directly, but can own assets

### Account Structure
```solidity
Account {
  nonce: uint64,           // Number of transactions sent
  balance: uint256,        // ETH balance in wei
  codeHash: bytes32,       // Hash of contract code
  storageRoot: bytes32     // Root of storage trie
}
```

## Transaction Model

### Transaction Types

#### Type 0: Legacy Transactions
```solidity
{
  nonce: uint,
  gasPrice: uint,
  gasLimit: uint,
  to: address,
  value: uint,
  data: bytes,
  v, r, s: signature
}
```

#### Type 1: Access List Transactions (EIP-2930)
```solidity
{
  chainId: uint,
  nonce: uint,
  gasPrice: uint,
  gasLimit: uint,
  to: address,
  value: uint,
  data: bytes,
  accessList: [
    {
      address: address,
      storageKeys: bytes32[]
    }
  ],
  v, r, s: signature
}
```

#### Type 2: Dynamic Fee Transactions (EIP-1559)
```solidity
{
  chainId: uint,
  nonce: uint,
  maxPriorityFeePerGas: uint,
  maxFeePerGas: uint,
  gasLimit: uint,
  to: address,
  value: uint,
  data: bytes,
  accessList: [...],
  v, r, s: signature
}
```

## Block Structure

### Block Header
```solidity
BlockHeader {
  parentHash: bytes32,          // Previous block's hash
  unclesHash: bytes32,          // Hash of uncle blocks
  coinbase: address,            // Miner/validator address
  stateRoot: bytes32,           // Root of state trie
  transactionsRoot: bytes32,    // Root of transaction trie
  receiptsRoot: bytes32,        // Root of receipts trie
  logsBloom: bytes256,          // Filter for event logs
  difficulty: uint,             // Mining difficulty
  number: uint,                 // Block number
  gasLimit: uint,               // Maximum gas allowed
  gasUsed: uint,                // Gas consumed
  timestamp: uint,              // Creation time
  extraData: bytes,             // Extra data field
  mixHash: bytes32,             // Proof of Work data
  nonce: uint64                 // Proof of Work nonce
}
```

### Block Composition
```
Block = BlockHeader + Transactions + Uncles
Total size: ~30-100 KB typical
```

## State Trees

### Merkle Patricia Trie (MPT)
- Modified Merkle tree structure
- Optimized for Ethereum's key-value data
- Branches (16 children), extensions, leaves
- Efficient updates and proofs

### State Root
- Root hash of MPT containing all accounts
- Changes with every transaction
- Allows nodes to verify state consistency
- Stored in block header

### Storage Trie
- Separate trie for each contract's storage
- Maps storage keys to values
- storageRoot stored in account

## Receipt and Logs

### Transaction Receipt
```solidity
Receipt {
  transactionHash: bytes32,
  blockNumber: uint,
  blockHash: bytes32,
  cumulativeGasUsed: uint,
  gasUsed: uint,
  contractAddress: address,     // For deployments
  logs: Log[],
  status: uint8,                // 1 = success, 0 = revert
  logsBloom: bytes256           // For log filtering
}
```

### Event Logs
- Emitted during contract execution
- NOT stored in state, only in logs
- Indexed for efficient querying
- Accessible to off-chain applications

```solidity
event Transfer(
  indexed address from,
  indexed address to,
  uint256 value
);
```

## Gas Model

### What is Gas?
- Unit of computation cost
- Every operation costs gas
- Prevents infinite loops
- Incentivizes efficient code

### Gas Costs (Examples)
- STOP: 0 gas
- ADD/SUB: 3 gas
- SLOAD: 2100 gas (warm) or 100 gas (cold)
- SSTORE: 20000 gas (write) or 5000 gas (update)
- CALL: 700+ gas
- KECCAK256: 30 gas + 6 gas per word

### EIP-1559: Dynamic Fees
- Separates base fee from priority fee
- Base fee: Determined by network congestion
- Priority fee: Tip for validators
- Total: (baseFee + priorityFee) * gasUsed
- Base fee burned, not given to validators

## Consensus: Proof of Stake (Post-Merge)

### Validators
- Stake 32 ETH minimum
- Randomly selected to propose blocks
- Earn rewards for honest participation
- Slashed for malicious behavior

### Epochs and Slots
- 1 Epoch = 32 Slots
- 1 Slot = 12 seconds
- 1 Epoch ≈ 6.4 minutes

### Finality
- Practical finality: 2 epochs (12.8 minutes)
- No block reversal after finality
- More efficient than PoW

## Sharding (Future)

### Purpose
- Increase throughput by dividing data
- Each shard handles subset of transactions
- Coordinated by beacon chain

### Key Components
- **Beacon Chain**: Coordinates shards
- **Shard Blocks**: Data committed to beacon chain
- **Light Clients**: Can verify with minimal data

## EVM Versions and Upgrades

### Notable Upgrades
- **Istanbul (Dec 2019)**: Gas cost changes
- **Berlin (Apr 2021)**: EIP-2929 access lists
- **London (Aug 2021)**: EIP-1559 dynamic fees
- **Merge (Sep 2022)**: Transition to PoS
- **Shanghai (Apr 2023)**: Staking withdrawals
- **Dencun (Mar 2024)**: Blob data, L2 scaling

## Network Parameters

### Mainnet
- ChainID: 1
- Block time: 12 seconds
- Gas limit: ~30 million
- Difficulty bomb: Disabled
- Current epoch: ~225,000+ (as of 2024)

### Testnets
- **Sepolia**: Latest, most stable
- **Goerli**: Being deprecated
- **Holesky**: PoS testnet
- **Mainnet fork**: Local testing

## Common Patterns

### Fallback Function
```solidity
fallback() external payable {
  // Handles unknown function calls
}

receive() external payable {
  // Handles plain ETH transfers
}
```

### Constructor
```solidity
constructor() {
  // Executed once at deployment
  // Sets up initial state
}
```

### Modifiers and Access Control
```solidity
modifier onlyOwner() {
  require(msg.sender == owner);
  _;
}
```

---

**Key Takeaways**:
- EVM executes smart contracts deterministically
- Account model with external and contract accounts
- Multiple transaction types for different use cases
- MPT enables efficient state verification
- Gas model incentivizes efficiency
- Proof of Stake provides finality and security
