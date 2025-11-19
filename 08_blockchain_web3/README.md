# Blockchain & Web3 Development Skill

**Elite-level guidance for building secure, scalable blockchain applications**

---

## 🎯 Overview

This Claude Code skill provides comprehensive expertise in blockchain and Web3 development, covering the complete development lifecycle from smart contract architecture to production deployment. Whether you're building DeFi protocols, NFT systems, or decentralized applications, this skill guides you through best practices, security considerations, and production-ready implementations.

### What This Skill Covers

- ✅ **Smart Contract Development**: Solidity, Vyper, Rust, security patterns, gas optimization
- ✅ **DeFi Protocol Engineering**: AMMs, lending protocols, yield aggregators, tokenomics
- ✅ **NFT Systems**: ERC-721/1155, marketplaces, dynamic metadata, composability
- ✅ **Layer 2 & Scaling**: Rollups, sidechains, bridges, cross-chain architecture
- ✅ **Web3 Frontend**: ethers.js, viem, wagmi, wallet integration, transaction management
- ✅ **Security & Auditing**: Vulnerability assessment, testing strategies, audit preparation
- ✅ **Testing Frameworks**: Foundry, Hardhat, fork testing, invariant testing
- ✅ **Deployment & Operations**: Multi-stage deployment, upgrades, monitoring

---

## 🚀 Quick Start

### Invoking the Skill

In Claude Code, reference this skill for blockchain development guidance:

```
Using the blockchain skill, help me build a secure NFT marketplace with royalty enforcement.
```

Or for specific tasks:

```
Using the blockchain skill, review this smart contract for security vulnerabilities.
```

```
Using the blockchain skill, implement a gas-optimized ERC-20 token with staking.
```

---

## 💡 Use Cases

### 1. Building a DeFi Protocol

**Example Request:**
> "I want to build an AMM-based DEX similar to Uniswap but with dynamic fees based on volatility. Guide me through the architecture and implementation."

**What You'll Get:**
- Complete architecture design with security considerations
- Smart contract implementation with gas optimization
- Comprehensive testing strategy
- Integration with price oracles
- Frontend Web3 integration code
- Deployment and monitoring setup

---

### 2. Creating an NFT Collection

**Example Request:**
> "Help me create a 10,000 NFT collection with on-chain traits, staking rewards, and marketplace royalties."

**What You'll Get:**
- ERC-721 contract with optimized minting
- On-chain randomness for trait generation
- Staking mechanism implementation
- ERC-2981 royalty standard integration
- IPFS metadata strategy
- Reveal mechanism and rarity calculation
- Web3 minting interface

---

### 3. Security Audit & Review

**Example Request:**
> "Review this lending protocol contract for security vulnerabilities and gas optimization opportunities."

**What You'll Get:**
- Comprehensive security analysis
- Re-entrancy, front-running, and oracle manipulation checks
- Access control verification
- Gas optimization recommendations
- Testing gaps identified
- Comparison with industry standards (Aave, Compound)
- Remediation priorities

---

### 4. Smart Contract Upgradeability

**Example Request:**
> "I need to upgrade my token contract to add new features without changing the address. What's the best approach?"

**What You'll Get:**
- Comparison of proxy patterns (Transparent, UUPS, Diamond)
- Implementation of chosen pattern
- State migration strategy
- Upgrade testing on forked mainnet
- Governance integration (if needed)
- Rollback procedures
- Post-upgrade verification

---

### 5. DeFi Integration

**Example Request:**
> "How do I integrate Uniswap V3 into my protocol for automated token swaps?"

**What You'll Get:**
- Uniswap V3 router integration code
- Slippage protection implementation
- Price impact calculations
- MEV protection strategies
- Fork testing against mainnet state
- Error handling for failed swaps
- Gas optimization techniques

---

## 🏗️ Development Workflows

### Workflow 1: New Smart Contract Project

1. **Requirements Analysis**: Define use case, threat model, architecture
2. **Environment Setup**: Foundry/Hardhat configuration, dependencies
3. **Core Implementation**: Write contracts with security patterns
4. **Testing Suite**: Unit tests, integration tests, fork tests, invariant tests
5. **Gas Optimization**: Profile and optimize gas usage
6. **Security Review**: Internal audit, automated tools, external audit
7. **Deployment**: Testnet → Audit → Mainnet with verification
8. **Monitoring**: Set up event monitoring and alerts

### Workflow 2: DeFi Protocol Development

1. **Economic Design**: Tokenomics, incentive mechanisms, fee structures
2. **Architecture**: Core contracts, oracle integration, governance
3. **Implementation**: AMM/Lending/Yield logic with security first
4. **Advanced Testing**: Flash loan attacks, fork testing, economic simulations
5. **Oracle Integration**: Chainlink, Uniswap TWAP, or custom oracles
6. **Frontend**: Web3 interface with transaction management
7. **Audit**: Professional security audit
8. **Launch**: Gradual rollout with liquidity mining

### Workflow 3: NFT Project Launch

1. **Collection Design**: Supply, traits, utility, mechanics
2. **Contract Development**: ERC-721/1155, minting, metadata
3. **Metadata Strategy**: IPFS setup, on-chain data, reveal mechanism
4. **Marketplace Integration**: OpenSea, Blur, custom marketplace
5. **Minting Website**: Wallet connection, allowlist, public mint
6. **Testing**: Testnet mints, gas optimization, edge cases
7. **Launch Preparation**: Marketing, community, snapshot
8. **Post-Launch**: Royalty enforcement, secondary market monitoring

---

## 🔧 Common Tasks

### Task: Deploy an ERC-20 Token

```
Using the blockchain skill, create a production-ready ERC-20 token with:
- Initial supply of 1,000,000 tokens
- Burn mechanism
- Permit functionality (EIP-2612)
- Access control for minting
- Complete test suite
```

**Output**: Contracts, tests, deployment script, verification guide

---

### Task: Build a Staking Contract

```
Using the blockchain skill, implement a staking contract where:
- Users stake Token A to earn Token B
- Rewards calculated per block
- Emergency withdrawal option
- No lock period
- Protection against flash loan exploits
```

**Output**: Staking contract, reward calculation logic, tests, frontend integration

---

### Task: Create an NFT Marketplace

```
Using the blockchain skill, build an NFT marketplace with:
- Fixed price listings
- English auctions
- Royalty enforcement (ERC-2981)
- Multi-token support (ERC-721 and ERC-1155)
- Offer system
```

**Output**: Marketplace contracts, testing suite, Web3 interface examples

---

### Task: Implement a Lending Pool

```
Using the blockchain skill, create a lending pool similar to Aave where:
- Users can supply collateral and borrow
- Interest rates adjust based on utilization
- Liquidation at 80% loan-to-value
- Flash loans enabled
- Multiple asset support
```

**Output**: Core lending logic, interest rate model, liquidation system, tests

---

## 📚 Knowledge Areas

### Smart Contract Languages

**Solidity** (Primary)
- Syntax, data types, storage layout
- Security patterns and anti-patterns
- Gas optimization techniques
- Upgradeable contract patterns
- Assembly when needed

**Vyper**
- Pythonic syntax, security-first design
- When to choose Vyper over Solidity
- Limitations and trade-offs

**Rust** (Solana, NEAR)
- Program architecture
- Account model vs EVM model
- PDAs and cross-program invocation

### DeFi Mechanisms

**Automated Market Makers (AMMs)**
- Constant product formula (x * y = k)
- Concentrated liquidity (Uniswap V3)
- Stable swaps (Curve)
- Dynamic fees and MEV protection

**Lending & Borrowing**
- Supply/borrow mechanics
- Interest rate models
- Collateral factors and liquidation
- Flash loans

**Yield Optimization**
- Vault strategies
- Auto-compounding
- Strategy allocation
- Harvest automation

**Derivatives**
- Options protocols
- Perpetual futures
- Synthetic assets
- Oracle dependencies

### NFT Standards & Patterns

**ERC-721**: Non-fungible tokens
**ERC-1155**: Multi-token standard
**ERC-2981**: Royalty standard
**ERC-4907**: Rental NFTs
**ERC-6551**: Token-bound accounts

### Security Best Practices

**Common Vulnerabilities**
- Re-entrancy attacks
- Front-running and MEV
- Oracle manipulation
- Access control failures
- Integer overflow/underflow
- Flash loan attacks
- Denial of service

**Prevention Patterns**
- Checks-Effects-Interactions
- Pull over Push payments
- Circuit breakers
- Rate limiting
- Reentrancy guards
- Access control modifiers

**Testing Strategies**
- Unit testing all functions
- Integration testing workflows
- Fork testing against mainnet
- Invariant/property testing
- Fuzzing edge cases
- Attack scenario testing

### Web3 Frontend

**Libraries**
- **ethers.js**: Comprehensive Ethereum library
- **viem**: Type-safe, lightweight, fast
- **wagmi**: React hooks for Ethereum
- **web3.js**: Original Web3 library
- **@web3-react**: React Web3 provider

**Wallet Integration**
- MetaMask, WalletConnect, Coinbase Wallet
- Multi-wallet support
- Network switching
- Transaction signing

**State Management**
- Contract state syncing
- Pending transaction tracking
- Event listening and updates
- Optimistic UI updates

### Layer 2 & Scaling

**Optimistic Rollups**
- Optimism, Arbitrum
- Challenge periods
- Bridging assets
- EVM equivalence

**ZK-Rollups**
- zkSync, StarkNet, Polygon zkEVM
- Zero-knowledge proofs
- Finality and security
- Developer experience

**Sidechains & Alt-L1s**
- Polygon, Gnosis Chain, BNB Chain
- Security trade-offs
- Bridge architecture

### Development Tools

**Frameworks**
- **Foundry**: Fast, Solidity-native testing
- **Hardhat**: TypeScript ecosystem
- **Truffle**: Pioneer framework
- **Brownie**: Python-based

**Security Tools**
- **Slither**: Static analysis
- **Mythril**: Symbolic execution
- **Echidna**: Smart fuzzing
- **Manticore**: Symbolic execution
- **Certora**: Formal verification

**Utilities**
- **Tenderly**: Debugging and simulation
- **The Graph**: Indexing blockchain data
- **Etherscan**: Block explorer and verification
- **Sourcify**: Decentralized source verification

---

## 🎓 Learning Path

### Beginner → Intermediate

1. **Blockchain Basics**: Understand blocks, transactions, consensus
2. **Solidity Fundamentals**: Variables, functions, modifiers, events
3. **First Smart Contract**: Simple token or voting contract
4. **Testing Basics**: Write unit tests with Foundry/Hardhat
5. **Deployment**: Deploy to testnet, verify on Etherscan
6. **Web3 Integration**: Build a simple frontend

### Intermediate → Advanced

1. **Security Patterns**: Learn common vulnerabilities and mitigations
2. **DeFi Mechanisms**: Build an AMM or lending protocol
3. **Gas Optimization**: Profile and optimize contracts
4. **Upgradeability**: Implement proxy patterns
5. **Advanced Testing**: Fork tests, invariant tests, attack scenarios
6. **Production Deployment**: Multi-sig, monitoring, incident response

### Advanced → Expert

1. **Protocol Design**: Economic mechanisms, game theory
2. **Formal Verification**: Mathematical proofs of correctness
3. **MEV & Front-running**: Understanding and mitigation
4. **Cross-chain**: Bridge architecture, security considerations
5. **Auditing**: Learn to audit other projects professionally
6. **Research**: Stay current with new EIPs and protocols

---

## 🔒 Security Emphasis

This skill **strongly emphasizes security** at every stage:

### Pre-Development
- Threat modeling
- Economic attack vectors
- Access control design
- Upgradeability considerations

### During Development
- Security-first coding patterns
- Gas optimization (less code = less attack surface)
- Comprehensive natspec comments
- Clear error messages

### Testing
- Attack scenario testing
- Fork testing against real protocols
- Invariant testing
- Fuzzing edge cases

### Pre-Deployment
- Internal code review
- Automated security tools
- External audit
- Bug bounty preparation

### Post-Deployment
- Monitoring and alerts
- Incident response plan
- Upgrade procedures
- Community communication

---

## 🌐 Multi-Chain Support

This skill covers development across multiple blockchain ecosystems:

**EVM Chains**
- Ethereum, Polygon, Arbitrum, Optimism, BSC, Avalanche
- EVM equivalence and differences
- Gas optimization per chain

**Non-EVM Chains**
- Solana (Rust/Anchor)
- NEAR (Rust/AssemblyScript)
- Aptos/Sui (Move)
- Cosmos SDK

**Layer 2 Specific**
- zkSync (Solidity with modifications)
- StarkNet (Cairo)
- Optimism/Arbitrum (EVM-compatible)

---

## 📊 Example Outputs

### Example 1: Security Review

**Input:**
```solidity
contract SimpleBank {
    mapping(address => uint) public balances;

    function withdraw() public {
        uint amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;
    }
}
```

**Output:**
```
🚨 CRITICAL: Re-entrancy Vulnerability

The withdraw function is vulnerable to re-entrancy attacks.

Issue: State update (balances[msg.sender] = 0) happens AFTER external call

Attack scenario:
1. Attacker's contract calls withdraw()
2. Receive function calls withdraw() again
3. Balance check passes (still non-zero)
4. Double withdrawal succeeds

Fix: Follow Checks-Effects-Interactions pattern
[Provides fixed code with ReentrancyGuard]

Additional recommendations:
- Use pull payment pattern
- Add emergency pause
- Implement withdrawal limits
[Full detailed analysis...]
```

---

### Example 2: DeFi Protocol Implementation

**Input:**
> "Build a simple AMM for two tokens"

**Output:**
- Complete AMM contract with:
  - Constant product formula
  - Add/remove liquidity
  - Swap function with slippage
  - LP token minting
  - Fee mechanism
- Comprehensive test suite (50+ tests)
- Gas optimization report
- Integration with frontend
- Deployment script
- Monitoring setup

---

### Example 3: NFT with Utility

**Input:**
> "Create an NFT that grants governance rights and staking rewards"

**Output:**
- ERC-721 contract with voting power
- Staking contract with reward distribution
- Snapshot integration for off-chain voting
- Dynamic metadata showing staking status
- Web3 interface for staking/unstaking
- Test suite covering all mechanics
- Gas profiling and optimization

---

## 🛠️ Integration with Other Skills

This blockchain skill works great with:

- **Cloud Skills**: Deploy nodes, IPFS, monitoring infrastructure
- **Security Skills**: Penetration testing, vulnerability assessment
- **Frontend Skills**: React/Next.js Web3 interfaces
- **Database Skills**: Indexing blockchain data with The Graph
- **DevOps Skills**: CI/CD for smart contracts, automated testing

---

## 📖 Best Practices Applied

1. **Security First**: Every recommendation prioritizes security
2. **Gas Efficiency**: Optimizations suggested proactively
3. **Testing Rigor**: Comprehensive test coverage expected
4. **Standards Compliance**: Follows established EIPs
5. **Documentation**: Clear natspec and inline comments
6. **Upgradeability**: Future-proofing considered
7. **Monitoring**: Observability built-in
8. **User Safety**: Protects users from common mistakes

---

## 🎯 When to Use This Skill

### Perfect For:
- Building DeFi protocols from scratch
- Creating NFT collections and marketplaces
- Auditing smart contracts for security
- Optimizing gas usage in existing contracts
- Integrating Web3 into applications
- Learning blockchain development best practices
- Preparing for security audits
- Implementing upgradeable contract systems

### Also Useful For:
- Understanding DeFi protocol mechanics
- Researching new blockchain technologies
- Evaluating different L2 solutions
- Designing tokenomics and incentive systems
- Troubleshooting Web3 integration issues
- Planning deployment strategies

---

## 💼 Professional Standards

This skill follows industry-leading practices from:

- **OpenZeppelin**: Battle-tested contract libraries
- **Trail of Bits**: Security audit methodology
- **Consensys**: Smart contract best practices
- **FAANG**: Large-scale system design
- **Top DeFi Protocols**: Uniswap, Aave, Compound architecture
- **Security Researchers**: Samczsun, OpenZeppelin, Trail of Bits findings

---

## 🚨 Important Disclaimers

1. **Audit Requirement**: Always get professional audits for production contracts handling real value
2. **Test Thoroughly**: Blockchain transactions are irreversible
3. **Start Small**: Deploy with limited funds initially
4. **Bug Bounties**: Consider bug bounty programs for production code
5. **Regulatory Compliance**: Consult legal experts for regulatory requirements
6. **No Guarantees**: This skill provides guidance, not guarantees of security

---

## 📞 Getting Help

For blockchain-specific questions:
1. Describe your use case and requirements
2. Share relevant code (if any)
3. Specify target blockchain(s)
4. Mention security considerations
5. Indicate timeline and audit status

The skill will provide tailored, security-focused guidance for your specific needs.

---

## 🎉 Ready to Build?

Start with a clear description of what you want to build:

```
Using the blockchain skill, I want to create [description of your project]
```

The skill will guide you through architecture, implementation, testing, security, and deployment with production-ready code and best practices every step of the way.

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintainer**: Elite Blockchain Development Standards
**License**: MIT
**Blockchain Focus**: EVM-compatible chains (Ethereum, Polygon, Arbitrum, Optimism, etc.)

---

**Remember**: Blockchain development requires extreme attention to security. Take your time, test thoroughly, and always get audits for production code. 🔒
