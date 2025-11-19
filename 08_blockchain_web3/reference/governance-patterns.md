# Governance Patterns

## Token-Based Governance (Compound/Uniswap)

```solidity
contract Governor {
    struct Proposal {
        uint id;
        address proposer;
        uint eta;
        address[] targets;
        uint[] values;
        string[] signatures;
        bytes[] calldatas;
        uint startBlock;
        uint endBlock;
        uint forVotes;
        uint againstVotes;
        bool canceled;
        bool executed;
        mapping(address => Receipt) receipts;
    }

    struct Receipt {
        bool hasVoted;
        bool support;
        uint96 votes;
    }

    function propose(...) external returns (uint);
    function castVote(uint proposalId, bool support) external;
    function execute(uint proposalId) external;
}
```

## Key Parameters
- **Proposal Threshold**: Min tokens to propose (1% supply)
- **Quorum**: Min participation (4% supply)
- **Voting Period**: 3-7 days
- **Timelock**: 2-7 days before execution

## Delegation
```solidity
mapping(address => address) public delegates;

function delegate(address delegatee) external {
    delegates[msg.sender] = delegatee;
}

function getVotes(address account) public view returns (uint) {
    // Return voting power including delegations
}
```

## Snapshot Voting
- Off-chain voting
- Gasless
- IPFS storage
- Execution requires on-chain multisig

## Optimistic Governance
- Proposals auto-execute unless challenged
- Challenge period (e.g., 7 days)
- Security council can veto
