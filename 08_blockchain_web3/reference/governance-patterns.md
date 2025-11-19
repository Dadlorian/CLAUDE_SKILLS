# Governance Patterns in DeFi

## Overview

Governance determines how protocols evolve, adapt to market conditions, and distribute power. Different governance models offer trade-offs between decentralization, speed, and security. This guide covers governance architectures used by leading DeFi protocols and their implementation patterns.

Effective governance is critical because it directly impacts:
- Protocol security and upgrade decisions
- Fee structures and economic parameters
- Treasury management and value distribution
- Protocol roadmap and feature prioritization

## Core Governance Models

### 1. Token-Based Voting (Compound/Uniswap)

**Model**: One token = one vote, voting power can be delegated

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorSettings.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Votes.sol";

contract ProtocolGovernor is Governor, GovernorSettings {
    ERC20Votes public governanceToken;

    constructor(ERC20Votes _token)
        Governor("ProtocolGovernor")
        GovernorSettings(
            1,          // voting delay (1 block)
            50400,      // voting period (1 week on Ethereum)
            100e18      // proposal threshold (100 tokens)
        )
    {
        governanceToken = _token;
    }

    // Override required functions
    function votingDelay()
        public
        view
        override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.votingDelay();
    }

    function votingPeriod()
        public
        view
        override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.votingPeriod();
    }

    function quorumNumerator() public view virtual override returns (uint256) {
        return 4; // 4% quorum
    }

    function proposalThreshold()
        public
        view
        override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.proposalThreshold();
    }
}

// Example: Proposal struct
struct Proposal {
    uint256 id;
    address proposer;
    uint256 eta;                    // Timelock release time
    address[] targets;              // Contracts to call
    uint256[] values;               // ETH values
    string[] signatures;            // Function signatures
    bytes[] calldatas;              // Function parameters
    uint256 startBlock;             // Block voting starts
    uint256 endBlock;               // Block voting ends
    uint256 forVotes;               // Votes for
    uint256 againstVotes;           // Votes against
    uint256 abstainVotes;           // Votes abstain
    bool canceled;
    bool executed;
    mapping(address => Receipt) receipts;
}

struct Receipt {
    bool hasVoted;
    uint8 support;  // 0: Against, 1: For, 2: Abstain
    uint96 votes;
}
```

**Proposal Lifecycle**:
1. **Proposal Creation**: Proposer with sufficient tokens creates proposal (requires voting power delegation)
2. **Voting Delay**: 1 block (prevents sandwich attacks on voting power)
3. **Active Voting**: 50,400 blocks (~1 week) for community to vote
4. **Timelock**: 2-7 day delay before execution
5. **Execution**: Proposal executes on-chain via Timelock contract

**Key Parameters**:
- **Proposal Threshold**: Min tokens required to propose (1-5% of supply)
- **Quorum**: Minimum participation required (4-10% of total votes)
- **Voting Period**: 3-7 days for voting
- **Timelock Delay**: 2-7 days before execution (allows exit/circuit breaks)

### 2. Vote Delegation

**Purpose**: Token holders delegate voting power without transferring tokens

```solidity
contract VotingTokenWithDelegation is ERC20Votes {
    constructor(string memory name, string memory symbol)
        ERC20(name, symbol)
        ERC20Permit(name)
    {}

    // Users call this to delegate their votes
    function delegate(address delegatee) public virtual override {
        address currentDelegate = delegates(msg.sender);

        // Can delegate to self to activate voting power
        super.delegate(delegatee);

        emit DelegateChanged(msg.sender, currentDelegate, delegatee);
    }

    function delegateBySig(
        address delegatee,
        uint256 nonce,
        uint256 expiry,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public virtual override {
        bytes32 domainSeparator = _domainSeparatorV4();
        bytes32 structHash = keccak256(
            abi.encode(_DELEGATE_TYPEHASH, delegatee, nonce, expiry)
        );
        bytes32 digest = _hashTypedDataV4(structHash);
        address signatory = ecrecover(digest, v, r, s);

        require(signatory != address(0), "Invalid signature");
        require(expiry >= block.timestamp, "Signature expired");

        super.delegate(delegatee);
    }

    // View voting power at past block
    function getPriorVotes(address account, uint256 blockNumber)
        public
        view
        returns (uint256)
    {
        return getPastVotes(account, blockNumber);
    }
}
```

**Delegation Features**:
- Voting power must be **explicitly delegated** (not automatic)
- Can self-delegate to activate voting rights
- Supports EIP-712 signatures for gasless delegation
- Voting power calculated at snapshot block (prevents flash loan attacks)

### 3. Snapshot Voting (Off-Chain)

**Model**: Off-chain voting with on-chain execution via multisig

```javascript
// Example: Using Snapshot.org for governance
{
    "space": "protocol.eth",
    "type": "single-choice",
    "title": "Increase fee to 0.5%",
    "body": "This proposal increases swap fees from 0.3% to 0.5% to fund protocol development",
    "choices": ["For", "Against", "Abstain"],
    "start": 1234567890,
    "end": 1234654290,
    "snapshot": 16000000,  // Block for voting power calculation
    "plugins": {
        "safeSnap": {
            "execution": [
                {
                    "to": "0x1111111254fb6c44bac0bed2854e76f90643097d",
                    "data": "0x...",  // Contract call
                    "value": "0"
                }
            ]
        }
    }
}
```

**Advantages**:
- Gasless voting for participants
- Flexible voting options
- Easy to understand proposals
- Uses IPFS for storing proposal details

**Execution Flow**:
1. Community votes off-chain on Snapshot
2. Results verified and signed
3. Multisig executes approved proposals on-chain

### 4. Optimistic Governance

**Model**: Proposals auto-execute unless challenged

```solidity
contract OptimisticGovernance {
    mapping(bytes32 => ProposalData) public proposals;
    uint256 public challengePeriod = 7 days;
    address public securityCouncil;

    struct ProposalData {
        bytes proposalData;
        uint256 submitBlock;
        bool executed;
        bool challenged;
        uint256 challengeDeposit;
    }

    event ProposalSubmitted(bytes32 indexed proposalHash, bytes proposal);
    event ProposalChallenged(bytes32 indexed proposalHash);
    event ProposalExecuted(bytes32 indexed proposalHash);

    function submitProposal(bytes calldata proposalData) external {
        require(msg.sender == governanceToken.holder(), "Only token holders");

        bytes32 proposalHash = keccak256(proposalData);
        proposals[proposalHash] = ProposalData({
            proposalData: proposalData,
            submitBlock: block.number,
            executed: false,
            challenged: false,
            challengeDeposit: 0
        });

        emit ProposalSubmitted(proposalHash, proposalData);
    }

    function executeProposal(bytes calldata proposalData) external {
        bytes32 proposalHash = keccak256(proposalData);
        ProposalData storage proposal = proposals[proposalHash];

        require(!proposal.executed, "Already executed");
        require(!proposal.challenged, "Proposal challenged");
        require(
            block.number >= proposal.submitBlock + challengePeriod,
            "Challenge period not elapsed"
        );

        proposal.executed = true;

        // Execute the proposal
        (bool success, ) = address(this).call(proposal.proposalData);
        require(success, "Execution failed");

        emit ProposalExecuted(proposalHash);
    }

    function challengeProposal(
        bytes32 proposalHash,
        string calldata reason
    ) external {
        require(msg.sender == securityCouncil, "Only security council");
        require(!proposals[proposalHash].executed, "Already executed");

        proposals[proposalHash].challenged = true;

        emit ProposalChallenged(proposalHash);
    }
}
```

**Advantages**:
- Fast governance (minutes instead of weeks)
- Lower participation friction
- Security council can veto dangerous proposals

**Risks**:
- Requires vigilant community monitoring
- Less time to react for token holders
- Relies on security council integrity

### 5. Vote Escrow (veToken) Model (Curve)

**Model**: Users lock tokens for voting power proportional to lock duration

```solidity
contract VeToken is ERC20 {
    mapping(address => LockedBalance) public locked;

    struct LockedBalance {
        int128 amount;
        uint256 end;
    }

    function create_lock(
        uint256 _value,
        uint256 _unlock_time
    ) external returns (uint256) {
        require(_unlock_time > block.timestamp, "Can't lock in past");
        require(_unlock_time <= block.timestamp + 4 * 365 days, "Max lock 4 years");

        LockedBalance storage locked_balance = locked[msg.sender];
        require(locked_balance.amount == 0, "Existing lock");

        _token.transferFrom(msg.sender, address(this), _value);

        locked_balance.amount = int128(_value);
        locked_balance.end = _unlock_time;

        return _balance_of_nft(msg.sender);
    }

    function voting_power_at(address account, uint256 ts)
        public
        view
        returns (uint256)
    {
        LockedBalance memory locked_balance = locked[account];

        if (ts > locked_balance.end) {
            return 0;
        }

        // Power decays linearly to zero at unlock time
        uint256 duration = locked_balance.end - ts;
        return (uint256(locked_balance.amount) * duration) / (4 * 365 days);
    }
}
```

**Incentives**:
- Longer locks = more voting power
- Encourages long-term protocol alignment
- **ve** holders receive protocol fees/rewards
- Creates friction for short-term governance attacks

## Governance Best Practices

### Security Measures

1. **Voting Delay**: Prevents same-block proposal + voting
2. **Block Snapshots**: Voting power at past block (prevents flash loans)
3. **Timelock**: Delay before execution (allows circuit breaks)
4. **Multisig Safety**: Critical parameters require multisig approval

```solidity
// Security best practices
contract SecureGovernance {
    // 1. Critical functions require 2-day timelock
    mapping(bytes32 => uint256) public timelocks;
    uint256 constant TIMELOCK_DELAY = 2 days;

    // 2. Parameter changes limited to reasonable bounds
    function setFeePercentage(uint256 newFee) external onlyGovernance {
        require(newFee <= 10, "Fee too high");  // Max 1%
        require(newFee >= 1, "Fee too low");    // Min 0.01%

        timelocks[keccak256(abi.encode("fee", newFee))] = block.timestamp;
    }

    // 3. Execution requires waiting period
    function executeFeeChange(uint256 newFee) external {
        bytes32 actionHash = keccak256(abi.encode("fee", newFee));
        require(
            block.timestamp >= timelocks[actionHash] + TIMELOCK_DELAY,
            "Timelock not elapsed"
        );

        feePercentage = newFee;
    }
}
```

### Monitoring & Analysis

- **Track voting participation** over time
- **Monitor power concentration** (top 10 voters)
- **Analyze proposal outcomes** (approved vs rejected)
- **Alert on unusual patterns** (whale voting)

### Governance Gas Costs

Typical governance costs on Ethereum mainnet:
- **Delegation**: ~80,000 gas ($5-50 per transaction)
- **Vote casting**: ~180,000 gas (~$15-100)
- **Proposal creation**: ~500,000 gas (~$50-200)

*Layer 2 costs are 100-1000x lower*

## Multi-Signature Alternative

For smaller protocols or early stage:

```solidity
contract MultiSigGovernance {
    address[] public signers;
    uint256 public requiredSignatures;

    mapping(bytes32 => Execution) public executions;

    struct Execution {
        address target;
        bytes data;
        uint256 signatureCount;
        mapping(address => bool) signed;
        bool executed;
    }

    function proposeExecution(address target, bytes calldata data) external {
        bytes32 executionHash = keccak256(abi.encode(target, data));
        require(!executions[executionHash].executed, "Already executed");
        executions[executionHash].target = target;
        executions[executionHash].data = data;
    }

    function signExecution(address target, bytes calldata data) external onlySigners {
        bytes32 executionHash = keccak256(abi.encode(target, data));
        require(!executions[executionHash].signed[msg.sender], "Already signed");

        executions[executionHash].signed[msg.sender] = true;
        executions[executionHash].signatureCount++;

        if (executions[executionHash].signatureCount >= requiredSignatures) {
            _execute(target, data);
        }
    }
}
```

## Governance Checklist

Design:
- [ ] Governance structure clearly defined
- [ ] Voting thresholds reasonable
- [ ] Timelock delays appropriate (2-7 days)
- [ ] Emergency procedures documented
- [ ] Parameter bounds enforced

Implementation:
- [ ] Vote delegation working
- [ ] Voting power calculation correct
- [ ] Proposal lifecycle clear
- [ ] Execution mechanism secure
- [ ] Event logging comprehensive

Monitoring:
- [ ] Governance dashboard active
- [ ] Voting participation tracked
- [ ] Proposal history archived
- [ ] Alerts configured for anomalies
- [ ] Community communication plan

---

**Remember**: Governance is how communities make decisions about protocols. Good governance is transparent, inclusive, and resistant to attacks.
