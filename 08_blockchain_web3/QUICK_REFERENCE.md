# Blockchain & Web3 Quick Reference

**Fast access to guides, templates, and references for blockchain development.**

---

## 📚 Main Documentation

- **[skill.md](skill.md)** - Complete development guide with security-first approach
- **[README.md](README.md)** - Usage instructions, examples, and workflows

---

## 📖 Comprehensive Guides

### Security & Testing
- **[Security Audit Checklist](guides/security-audit-checklist.md)** - Complete audit checklist with severity ratings
- **[Testing Strategies](guides/testing-strategies.md)** - Unit, integration, fork, and fuzz testing
- **[Gas Optimization](guides/gas-optimization.md)** - Comprehensive gas-saving techniques

---

## 🔧 Templates

### Smart Contracts
- **[Smart Contract Template](templates/smart-contract-template.md)**
  - Production-ready ERC-20 example
  - Foundry & Hardhat setup
  - Comprehensive test suite
  - Deployment scripts

### DeFi Protocols
- **[DeFi Protocol Template](templates/defi-protocol-template.md)**
  - AMM (Uniswap V2-style)
  - Lending pool (Aave/Compound-style)
  - Testing strategies for DeFi

### NFT Collections
- **[NFT Collection Template](templates/nft-collection-template.md)**
  - Advanced ERC-721 with all features
  - Allowlist minting (Merkle proofs)
  - Staking integration
  - ERC-1155 for gaming

### Web3 Frontend
- **[Web3 Frontend Template](templates/web3-frontend-template.md)**
  - Modern React + Next.js
  - wagmi + viem integration
  - Transaction management
  - NFT gallery & DeFi UI examples

---

## 🔍 Quick References

### Security
- **[Common Vulnerabilities](reference/common-vulnerabilities.md)** - 12 critical vulnerabilities with mitigations
  - Reentrancy
  - Integer overflow
  - Access control
  - Flash loan attacks
  - Oracle manipulation
  - And more...

### DeFi
- **[DeFi Patterns](reference/defi-patterns.md)** - Core DeFi mechanisms
  - AMM formulas (Uniswap V2/V3)
  - Lending protocols (Aave/Compound)
  - Yield aggregators
  - Stablecoin mechanisms

### Integration
- **[Oracle Integration](reference/oracle-integration.md)** - Chainlink, Uniswap TWAP
- **[Upgradeability Patterns](reference/upgradeability-patterns.md)** - Proxy patterns comparison
- **[Deployment Guide](reference/deployment-guide.md)** - Multi-chain deployment

### Advanced Topics
- **[MEV Protection](reference/mev-protection.md)** - Front-running and sandwich attack mitigation
- **[Governance Patterns](reference/governance-patterns.md)** - Token voting, delegation, timelocks
- **[Tokenomics](reference/tokenomics.md)** - Distribution, vesting, incentive design

### Standards & Tools
- **[ERC Standards](reference/erc-standards.md)** - ERC-20, 721, 1155, 2981, 4626, and more
- **[Tools & Frameworks](reference/tools-frameworks.md)** - Foundry, Hardhat, testing tools, libraries
- **[Best Practices](reference/best-practices.md)** - Security, gas, testing, deployment checklists

---

## 🚀 Quick Start Workflows

### New Smart Contract Project
1. Read: [Smart Contract Template](templates/smart-contract-template.md)
2. Use: [Best Practices](reference/best-practices.md)
3. Test: [Testing Strategies](guides/testing-strategies.md)
4. Optimize: [Gas Optimization](guides/gas-optimization.md)
5. Audit: [Security Audit Checklist](guides/security-audit-checklist.md)

### DeFi Protocol Development
1. Read: [DeFi Patterns](reference/defi-patterns.md)
2. Template: [DeFi Protocol Template](templates/defi-protocol-template.md)
3. Integrate: [Oracle Integration](reference/oracle-integration.md)
4. Protect: [MEV Protection](reference/mev-protection.md)
5. Test: Fork testing + invariant tests

### NFT Collection Launch
1. Template: [NFT Collection Template](templates/nft-collection-template.md)
2. Standards: [ERC Standards](reference/erc-standards.md) (ERC-721, 2981)
3. Frontend: [Web3 Frontend Template](templates/web3-frontend-template.md)
4. Deploy: [Deployment Guide](reference/deployment-guide.md)

### Security Review
1. Check: [Common Vulnerabilities](reference/common-vulnerabilities.md)
2. Audit: [Security Audit Checklist](guides/security-audit-checklist.md)
3. Test: [Testing Strategies](guides/testing-strategies.md)
4. Tools: Slither, Mythril, Echidna (see [Tools](reference/tools-frameworks.md))

---

## 📊 File Structure

```
08_blockchain_web3/
├── skill.md                          # Main skill prompt
├── README.md                          # User documentation
├── QUICK_REFERENCE.md                 # This file
│
├── guides/                            # Comprehensive guides
│   ├── security-audit-checklist.md   # Complete audit process
│   ├── gas-optimization.md           # Gas-saving techniques
│   └── testing-strategies.md         # Testing methodologies
│
├── templates/                         # Production-ready templates
│   ├── smart-contract-template.md    # ERC-20 + setup
│   ├── defi-protocol-template.md     # AMM + Lending
│   ├── nft-collection-template.md    # ERC-721/1155
│   └── web3-frontend-template.md     # React + wagmi
│
└── reference/                         # Quick references
    ├── common-vulnerabilities.md     # Security issues
    ├── defi-patterns.md              # DeFi mechanics
    ├── oracle-integration.md         # Oracle usage
    ├── upgradeability-patterns.md    # Proxy patterns
    ├── deployment-guide.md           # Multi-chain deploy
    ├── mev-protection.md             # MEV mitigation
    ├── governance-patterns.md        # DAO patterns
    ├── tokenomics.md                 # Token design
    ├── tools-frameworks.md           # Dev tools
    ├── erc-standards.md              # ERC specs
    └── best-practices.md             # Development standards
```

---

## 🎯 Common Tasks

| Task | Resources |
|------|-----------|
| **Create ERC-20 token** | [Smart Contract Template](templates/smart-contract-template.md) → [ERC Standards](reference/erc-standards.md) |
| **Build AMM** | [DeFi Protocol Template](templates/defi-protocol-template.md) → [DeFi Patterns](reference/defi-patterns.md) |
| **Launch NFT collection** | [NFT Template](templates/nft-collection-template.md) → [Web3 Frontend](templates/web3-frontend-template.md) |
| **Integrate Chainlink** | [Oracle Integration](reference/oracle-integration.md) |
| **Make contract upgradeable** | [Upgradeability Patterns](reference/upgradeability-patterns.md) |
| **Optimize gas** | [Gas Optimization](guides/gas-optimization.md) |
| **Security audit** | [Security Checklist](guides/security-audit-checklist.md) → [Vulnerabilities](reference/common-vulnerabilities.md) |
| **Write tests** | [Testing Strategies](guides/testing-strategies.md) |
| **Deploy multi-chain** | [Deployment Guide](reference/deployment-guide.md) |
| **Add governance** | [Governance Patterns](reference/governance-patterns.md) |

---

## 🔐 Security Quick Checks

Before deploying:
- [ ] Read [Common Vulnerabilities](reference/common-vulnerabilities.md)
- [ ] Complete [Security Audit Checklist](guides/security-audit-checklist.md)
- [ ] Run Slither: `slither .`
- [ ] Test coverage >95%: `forge coverage`
- [ ] Gas snapshot: `forge snapshot`
- [ ] External audit (for production)

---

## 💡 Pro Tips

1. **Start with templates** - Don't reinvent the wheel
2. **Security first** - Check vulnerabilities before writing code
3. **Test thoroughly** - Unit + integration + fork + fuzz
4. **Optimize gas** - But readability first
5. **Use established libraries** - OpenZeppelin for contracts
6. **Get audited** - Always for production code
7. **Monitor live contracts** - Use Tenderly or similar

---

## 📞 Need Help?

1. **Specific vulnerability?** → [Common Vulnerabilities](reference/common-vulnerabilities.md)
2. **DeFi mechanism?** → [DeFi Patterns](reference/defi-patterns.md)
3. **Gas too high?** → [Gas Optimization](guides/gas-optimization.md)
4. **Need a template?** → [Templates directory](templates/)
5. **General question?** → Start with [skill.md](skill.md) or [README.md](README.md)

---

**Last Updated**: 2025-11-19
**Version**: 1.0
**Skill**: Blockchain & Web3 Development
