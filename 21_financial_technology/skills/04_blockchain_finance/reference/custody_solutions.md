# Custody Solutions Reference

## What is Custody?

Safekeeping of digital assets on behalf of clients. Balances:
- Security: Asset protection
- Access: User ability to control/use assets
- Compliance: Regulatory requirements
- Usability: Ease of operation

## Custody Models

### Self-Custody (Non-Custodial)

#### How It Works
```
User owns private key
User controls funds directly
No intermediary
Full responsibility on user
```

#### Advantages
```
- No counterparty risk
- True ownership
- No regulatory burden
- No fees
- Full control
```

#### Disadvantages
```
- User must secure private key
- Loss/compromise: Permanent loss
- Backup management required
- No recovery if key lost
- Operational burden
```

#### Tools
```
MetaMask: Browser wallet
Ledger: Hardware wallet
Trezor: Hardware wallet
Electrum: Bitcoin wallet
```

### Custodial (Third-Party)

#### How It Works
```
User funds: To custody provider
Provider: Secures private keys
User: Has account/password access
Provider: Controls signing/transactions
```

#### Advantages
```
- Professional security
- Key recovery possible
- Compliance support
- Insurance options
- User convenience
```

#### Disadvantages
```
- Counterparty risk
- Provider failure: Loss possible
- Regulatory scrutiny
- Fees
- Delayed access possible
```

#### Examples
```
Coinbase Custody: Institutional custodian
Fidelity: Traditional finance entry
Gemini Custody: Crypto-focused
Kingdom Trust: Self-directed IRA custody
```

### Hybrid (Multi-Sig)

#### How It Works
```
Multiple keys required to move funds
Example: 2-of-3 multisig
  - User: Has 1 key
  - Provider: Has 1 key
  - Escrow agent: Has 1 key

Transaction: Needs 2+ signatures
```

#### Advantages
```
- Single key compromise: Insufficient
- User retains control
- Provider cannot unilaterally move funds
- Better than pure custodial
- Operational security
```

#### Disadvantages
```
- Complexity
- Slower transactions
- More infrastructure
- Implementation challenges
```

## Wallet Types

### Hardware Wallets

#### Features
```
Private keys: Stored offline
Signing: Happens on device
Physical device: Cannot be hacked remotely
Backup: Seed phrase recovery
```

#### Popular Options
```
Ledger: Most popular, broad support
Trezor: Open source, community trust
Coldcard: Bitcoin-focused
SafePal: More affordable option
```

#### Security
```
Private key: Never leaves device
Attack surface: Reduced
But: Physical device can be lost/stolen
Seed: Backup phrase needed (write down)
```

#### Best For
```
High-value holdings
Long-term storage
Security-conscious users
Institutional requirements
```

### Hot Wallets

#### Features
```
Private keys: On internet-connected device
Signing: Happens on device
Convenience: Quick access
Mobility: Mobile/web accessible
```

#### Popular Options
```
MetaMask: Browser extension
Trust Wallet: Mobile wallet
Rainbow: User-friendly mobile
Exodus: Desktop + mobile
```

#### Security
```
Private key: Exposed to device threats
Compromise risk: Higher than hardware
Malware: Can steal keys
Phishing: User social engineering
```

#### Best For
```
Small amounts
Frequent trading
Convenience-focused
Testing/development
```

### Smart Contract Wallets

#### How It Works
```
Wallet: Smart contract on blockchain
No private key: Account abstraction
Signing: Via recovery mechanisms
Multi-sig: Built-in
Social recovery: Via friends
```

#### Examples
```
Argent: Recovery via contacts
Gnosis Safe: Multi-sig contract
Safe (formerly Gnosis Safe): Institutional
Sequence: Gaming/NFT wallets
```

#### Advantages
```
- No seed phrase to lose
- Social recovery: Get account back via contacts
- Multi-sig built-in
- Programmable: Custom logic
- More accessible: No key management
```

#### Disadvantages
```
- Smart contract risk
- Gas costs: Operations more expensive
- Complexity: Harder to understand
- Newer: Less battle-tested
```

## Institutional Custody

### Regulatory Framework
```
Custody provider requirements:
- SEC/CFTC registration
- Insurance requirements
- Audit requirements
- Segregated accounts
- Controls and procedures
- Disaster recovery
```

### Key Requirements
```
Segregation: Client assets separate
Insurance: Coverage for losses
Audit: Regular third-party audits
Controls: Risk management procedures
Redundancy: Backup systems
```

### Institutional Custodians
```
Fidelity Digital Assets: Traditional finance
Kingdom Trust: Self-directed IRA
BitGo: Crypto-native provider
Coinbase Custody: Crypto exchange
Ledger Enterprise: Ledger for institutions
```

## Security Considerations

### Private Key Management
```
Generation:
- Randomness: Cryptographically secure
- No reuse: Each asset/account unique
- Diversity: Different algorithms

Storage:
- Offline: Hardware wallet
- Encrypted: Software wallet
- Distributed: Multi-sig/Shamir sharing
```

### Key Sharing (Shamir Secret Sharing)

#### How It Works
```
Secret: Private key
Split into N shares
Need M shares to reconstruct (M < N)

Example: 5 shares, need 3
1 share: Useless
2 shares: Useless
3+ shares: Can recover key

Advantage: No single point of failure
```

#### Example
```
5 shares generated
Distributed:
- Share 1: You
- Share 2: Safe deposit box
- Share 3: Family member
- Share 4: Legal advisor
- Share 5: Backup location

Recovery: Collect any 3 shares
```

### Backup Strategies

#### Seed Phrase
```
Standard: 12 or 24 words
Entropy: 128-256 bits of randomness
Recovery: Reconstruct any wallet with phrase
Storage: Physical backup (written)
Risk: Compromise = Loss of all funds
```

#### Encrypted Backups
```
Backup: Cloud encrypted
Encryption: User password protected
Access: Anywhere with password
Risk: Service provider risk
```

#### Offline Backups
```
Hardware: External drive/USB
Storage: Safe, offline location
Redundancy: Multiple copies
Protection: From theft/fire

Best practice: Multiple geographic locations
```

## Hot vs Cold Storage

### Cold Storage
```
Offline wallet: No internet
Security: Maximum
Access: Slower (need to bring online)
Best for: Long-term holding
Risk: Physical device risk
```

### Hot Storage
```
Online wallet: Internet connected
Security: Lower
Access: Instant
Best for: Active trading
Risk: Hacking/malware
```

### Typical Strategy
```
Large holdings: 90% cold storage (hardware wallet)
Active trading: 10% hot storage (exchange)
Daily use: Small amount in mobile wallet
Long-term: Hardware wallet or institutional custody
```

## Custody for DeFi

### Risks
```
Smart contract: Bugs in DeFi contracts
Liquidation: Collateral can be liquidated
Flash loans: Exploit your position
Oracle: Wrong price data
```

### Solutions
```
Insurance: Cover protocol failures
Self-custody: Use secure wallets
Monitor: Watch positions closely
Exit plan: Know how to unwind
Diversify: Multiple protocols
```

### Services
```
Ledger Live: Integrates DeFi
Argent: Built-in DeFi access
Safe: Multi-sig with DeFi
Instadapp: DeFi dashboard + custody
```

## Recovery Mechanisms

### Standard Recovery
```
Seed phrase: Restore from 12/24 words
New device: Same seed, new wallet
Recovery time: Minutes
Risk: If phrase compromised
```

### Social Recovery
```
Guardians: Trusted contacts
Help: Prove identity, authorize recovery
Advantages: No single point of failure
Time: Delay (voting period)
```

### Time-Locked Recovery
```
Delay: Period where owner can cancel
Mechanism: Prevents instant recovery
Security: Owner can react if compromised
Example: 1-week delay
```

## Compliance and Regulation

### Custody Regulation
```
US: SEC/CFTC jurisdiction
EU: MICA regulation (2024+)
Hong Kong: SFC regulation
Singapore: MAS regulation
```

### Requirements (MICA - EU)
```
- Professional safeguarding
- Insurance requirements
- Operational resilience
- Regular audits
- Business continuity
- Technology resilience
```

### Institutional vs Retail
```
Institutional: Highest regulatory requirements
Professional: Medium requirements
Retail: Minimal direct requirements
```

## Comparison: Custody Options

| Feature | Self-Custody | Hardware Wallet | Hot Wallet | Custodian | Smart Contract |
|---------|--------------|-----------------|-----------|-----------|----------------|
| Security | User-dependent | High | Medium | Institution | Medium |
| Convenience | Low | Medium | High | Medium | Medium |
| Recovery | No seed | Seed phrase | Seed/backup | Yes | Social |
| Cost | Free | $50-200 | Free | Fees | Gas fees |
| Control | Full | Full | Full | Limited | Full |
| Compromise Risk | High | Low | Medium | Counterparty | Smart contract |

## Best Practices

### For Individuals
```
1. Use hardware wallet for significant holdings
2. Back up seed phrase (multiple locations)
3. Test recovery process
4. Use strong passwords
5. Enable 2FA where applicable
6. Monitor accounts regularly
7. Use hardware wallet for transactions
```

### For Institutions
```
1. Use regulated custodian
2. Multi-sig requirement
3. Segregated accounts
4. Insurance coverage
5. Regular audits
6. Disaster recovery plans
7. Incident response procedures
```

### For DeFi Usage
```
1. Use smart contract wallet (if comfortable)
2. Keep keys secure
3. Monitor positions closely
4. Understand smart contract risks
5. Insurance: Consider coverage
6. Gradual entry: Learn as you go
7. Exit plan: Know how to unwind
```

## Emerging Solutions

### Account Abstraction
```
User accounts: Smart contracts
No private keys: Signature schemes flexible
Recovery: Programmable
DApps: Can sponsor gas fees
Status: EIP-4337 (Ethereum standard)
```

### Threshold Cryptography
```
Distributed key generation
No single point of compromise
Threshold: M of N shares needed
Applications: Custody, validator networks
```

### Zero-Knowledge Proofs
```
Privacy: Prove ownership without revealing key
Verification: Cryptographic proof
Applications: Wallet privacy, DeFi
```

## Moving Assets Safely

### Between Custody Types
```
Hardware → Exchange:
1. Generate address on exchange
2. Verify address on hardware device
3. Send small amount first
4. Verify receipt
5. Then send full amount

Exchange → Hardware:
1. Generate address on hardware
2. Note address
3. Withdraw from exchange to address
4. Verify receipt
5. Confirm on hardware device
```

### Between Blockchains
```
1. Use official bridge or established service
2. Start with small amount
3. Verify wrapped token contract
4. Confirm receipt
5. Then bridge full amount
```

---

**Key Takeaways**:
- Self-custody: Full control, full responsibility
- Hardware wallets: Best security for individuals
- Custodial: Professional security, counterparty risk
- Institutional custody: Required for regulated funds
- Multi-sig: Optimal balance of control and security
- Backup strategies: Critical for recovery
- Regulatory compliance: Increasingly important
- Choose based on use case and risk tolerance
