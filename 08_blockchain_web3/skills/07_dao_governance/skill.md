# DAO Governance

## Overview
Design and implement decentralized autonomous organizations (DAOs) with on-chain governance, voting mechanisms, treasury management, and decentralized decision-making systems.

## Governance Models

### 1. Token-Based Voting
- **One Token = One Vote**: Direct proportional voting
- **Quadratic Voting**: Square root of tokens held
- **Delegation**: Vote power assignment
- **Time-Weighted**: Longer holdings = more power
- **Conviction Voting**: Time-locked proposals

### 2. Multi-Sig Governance
- **Threshold Signatures**: M-of-N approval required
- **Role-Based**: Different roles, different powers
- **Gnosis Safe**: Popular multi-sig implementation
- **Emergency Powers**: Fast response capability

### 3. Hybrid Models
- **Council + Token**: Combined governance
- **Futarchy**: Prediction market governance
- **Holographic Consensus**: Attention-based prioritization
- **Optimistic Governance**: Execute unless vetoed

## Core Components

### 1. Governance Token
```solidity
contract GovernanceToken is ERC20Votes {
    constructor() ERC20("DAO Token", "DAO") ERC20Permit("DAO Token") {
        _mint(msg.sender, 1000000 * 10**decimals());
    }

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20Votes) {
        super._afterTokenTransfer(from, to, amount);
    }

    function _mint(address to, uint256 amount)
        internal override(ERC20Votes)
    {
        super._mint(to, amount);
    }

    function _burn(address account, uint256 amount)
        internal override(ERC20Votes)
    {
        super._burn(account, amount);
    }
}
```

### 2. Governor Contract
```solidity
contract DAOGovernor is Governor, GovernorSettings, GovernorCountingSimple,
    GovernorVotes, GovernorVotesQuorumFraction, GovernorTimelockControl
{
    constructor(
        IVotes _token,
        TimelockController _timelock
    )
        Governor("DAO Governor")
        GovernorSettings(
            1,      // 1 block voting delay
            50400,  // 1 week voting period
            0       // proposal threshold
        )
        GovernorVotes(_token)
        GovernorVotesQuorumFraction(4) // 4% quorum
        GovernorTimelockControl(_timelock)
    {}

    function votingDelay()
        public view override(IGovernor, GovernorSettings)
        returns (uint256)
    {
        return super.votingDelay();
    }

    function votingPeriod()
        public view override(IGovernor, GovernorSettings)
        returns (uint256)
    {
        return super.votingPeriod();
    }

    function quorum(uint256 blockNumber)
        public view override(IGovernor, GovernorVotesQuorumFraction)
        returns (uint256)
    {
        return super.quorum(blockNumber);
    }

    function proposalThreshold()
        public view override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.proposalThreshold();
    }

    function state(uint256 proposalId)
        public view override(Governor, GovernorTimelockControl)
        returns (ProposalState)
    {
        return super.state(proposalId);
    }

    function propose(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description
    ) public override(Governor, IGovernor) returns (uint256) {
        return super.propose(targets, values, calldatas, description);
    }

    function _execute(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) {
        super._execute(proposalId, targets, values, calldatas, descriptionHash);
    }

    function _cancel(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) returns (uint256) {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    function _executor()
        internal view override(Governor, GovernorTimelockControl)
        returns (address)
    {
        return super._executor();
    }

    function supportsInterface(bytes4 interfaceId)
        public view override(Governor, GovernorTimelockControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

### 3. Timelock Controller
```solidity
contract DAOTimelock is TimelockController {
    constructor(
        uint256 minDelay,
        address[] memory proposers,
        address[] memory executors,
        address admin
    ) TimelockController(minDelay, proposers, executors, admin) {}
}
```

## Proposal Lifecycle

### 1. Proposal Creation
```solidity
function createProposal(
    address[] memory targets,
    uint256[] memory values,
    bytes[] memory calldatas,
    string memory description
) public returns (uint256 proposalId) {
    require(
        getVotes(msg.sender, block.number - 1) >= proposalThreshold(),
        "Insufficient voting power"
    );

    proposalId = propose(targets, values, calldatas, description);

    emit ProposalCreated(
        proposalId,
        msg.sender,
        targets,
        values,
        calldatas,
        description
    );
}
```

### 2. Voting Process
```solidity
enum VoteType {
    Against,
    For,
    Abstain
}

function castVote(uint256 proposalId, uint8 support) public {
    require(state(proposalId) == ProposalState.Active, "Voting not active");

    uint256 weight = getVotes(msg.sender, proposalSnapshot(proposalId));
    require(weight > 0, "No voting power");

    _castVote(proposalId, msg.sender, support, "");
}

function castVoteWithReason(
    uint256 proposalId,
    uint8 support,
    string calldata reason
) public {
    uint256 weight = getVotes(msg.sender, proposalSnapshot(proposalId));
    _castVote(proposalId, msg.sender, support, reason);
}
```

### 3. Execution
```solidity
function executeProposal(
    uint256 proposalId,
    address[] memory targets,
    uint256[] memory values,
    bytes[] memory calldatas,
    bytes32 descriptionHash
) public payable {
    require(state(proposalId) == ProposalState.Succeeded, "Not succeeded");

    _execute(proposalId, targets, values, calldatas, descriptionHash);

    emit ProposalExecuted(proposalId);
}
```

## Treasury Management

### 1. Treasury Contract
```solidity
contract DAOTreasury is Ownable {
    event FundsReceived(address indexed from, uint256 amount);
    event FundsSpent(address indexed to, uint256 amount, string purpose);
    event TokensWithdrawn(address indexed token, address to, uint256 amount);

    receive() external payable {
        emit FundsReceived(msg.sender, msg.value);
    }

    function spend(
        address payable to,
        uint256 amount,
        string memory purpose
    ) external onlyOwner {
        require(address(this).balance >= amount, "Insufficient balance");

        (bool success, ) = to.call{value: amount}("");
        require(success, "Transfer failed");

        emit FundsSpent(to, amount, purpose);
    }

    function withdrawTokens(
        address token,
        address to,
        uint256 amount
    ) external onlyOwner {
        IERC20(token).transfer(to, amount);
        emit TokensWithdrawn(token, to, amount);
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getTokenBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
}
```

### 2. Budget Allocation
```solidity
struct Budget {
    string name;
    uint256 allocated;
    uint256 spent;
    uint256 endTime;
    address manager;
}

mapping(uint256 => Budget) public budgets;
uint256 public budgetCount;

function createBudget(
    string memory name,
    uint256 amount,
    uint256 duration,
    address manager
) external onlyGovernance returns (uint256) {
    budgetCount++;

    budgets[budgetCount] = Budget({
        name: name,
        allocated: amount,
        spent: 0,
        endTime: block.timestamp + duration,
        manager: manager
    });

    return budgetCount;
}

function spendFromBudget(
    uint256 budgetId,
    address to,
    uint256 amount
) external {
    Budget storage budget = budgets[budgetId];

    require(msg.sender == budget.manager, "Not budget manager");
    require(block.timestamp < budget.endTime, "Budget expired");
    require(budget.spent + amount <= budget.allocated, "Budget exceeded");

    budget.spent += amount;
    payable(to).transfer(amount);
}
```

## Delegation System

### 1. Vote Delegation
```solidity
mapping(address => address) public delegates;
mapping(address => uint256) public delegatedVotes;

event DelegateChanged(
    address indexed delegator,
    address indexed fromDelegate,
    address indexed toDelegate
);

function delegate(address delegatee) external {
    address currentDelegate = delegates[msg.sender];
    uint256 amount = balanceOf(msg.sender);

    delegates[msg.sender] = delegatee;

    if (currentDelegate != address(0)) {
        delegatedVotes[currentDelegate] -= amount;
    }

    if (delegatee != address(0)) {
        delegatedVotes[delegatee] += amount;
    }

    emit DelegateChanged(msg.sender, currentDelegate, delegatee);
}

function getVotes(address account) public view returns (uint256) {
    return balanceOf(account) + delegatedVotes[account];
}
```

### 2. Delegate Dashboard
```javascript
// Frontend delegation tracking
async function getDelegateInfo(address) {
    const delegates = await governor.delegates(address);
    const votingPower = await governor.getVotes(address);
    const proposals = await getActiveProposals();

    return {
        delegatedTo: delegates,
        votingPower,
        activeProposals: proposals.length
    };
}
```

## Voting Strategies

### 1. Quadratic Voting
```solidity
function getQuadraticVotingPower(address account, uint256 proposalId)
    public view returns (uint256)
{
    uint256 balance = getPastVotes(account, proposalSnapshot(proposalId));
    return sqrt(balance);
}

function sqrt(uint256 x) internal pure returns (uint256 y) {
    uint256 z = (x + 1) / 2;
    y = x;
    while (z < y) {
        y = z;
        z = (x / z + z) / 2;
    }
}
```

### 2. Conviction Voting
```solidity
struct ConvictionProposal {
    uint256 requestedAmount;
    address beneficiary;
    uint256 convictionLast;
    uint256 blockLast;
    mapping(address => uint256) voterStake;
}

function calculateConviction(
    uint256 timePassed,
    uint256 lastConv,
    uint256 oldAmount
) public pure returns (uint256) {
    // Exponential conviction growth
    return lastConv + (oldAmount * timePassed) / CONVICTION_PERIOD;
}
```

## Off-Chain Governance

### 1. Snapshot Integration
```javascript
// Create snapshot proposal
const proposal = {
    space: 'mydao.eth',
    type: 'single-choice',
    title: 'Proposal Title',
    body: 'Proposal description',
    choices: ['For', 'Against', 'Abstain'],
    start: Math.floor(Date.now() / 1000),
    end: Math.floor(Date.now() / 1000) + 604800, // 1 week
    snapshot: blockNumber
};

const receipt = await snapshot.createProposal(proposal);
```

### 2. IPFS Proposal Storage
```javascript
import { create } from 'ipfs-http-client';

const ipfs = create({ url: 'https://ipfs.infura.io:5001' });

async function storeProposal(proposal) {
    const { cid } = await ipfs.add(JSON.stringify(proposal));
    return `ipfs://${cid}`;
}
```

## Security Best Practices

### 1. Timelock Protection
- Minimum delay before execution
- Grace period for execution
- Cancellation mechanisms
- Emergency pause

### 2. Quorum Requirements
```solidity
function _quorumReached(uint256 proposalId)
    internal view returns (bool)
{
    ProposalVote storage proposalvote = _proposalVotes[proposalId];

    return quorum(proposalSnapshot(proposalId)) <=
        proposalvote.forVotes + proposalvote.abstainVotes;
}
```

### 3. Proposal Validation
```solidity
function _validateProposal(
    address[] memory targets,
    uint256[] memory values,
    bytes[] memory calldatas
) internal pure {
    require(targets.length == values.length, "Length mismatch");
    require(targets.length == calldatas.length, "Length mismatch");
    require(targets.length > 0, "Empty proposal");
    require(targets.length <= 10, "Too many actions");
}
```

## Analytics & Reporting

### 1. Participation Metrics
```solidity
struct GovernanceMetrics {
    uint256 totalProposals;
    uint256 passedProposals;
    uint256 failedProposals;
    uint256 totalVoters;
    uint256 averageParticipation;
}

function getMetrics() external view returns (GovernanceMetrics memory) {
    return metrics;
}
```

### 2. Voter Activity
```javascript
async function getVoterStats(address) {
    const votedProposals = await governor.queryFilter(
        governor.filters.VoteCast(null, address)
    );

    return {
        totalVotes: votedProposals.length,
        votingPower: await governor.getVotes(address),
        delegatedFrom: await getDelegators(address)
    };
}
```

## Resources

### Documentation
- OpenZeppelin Governor
- Compound Governor Bravo
- Snapshot Documentation
- Tally Documentation

### Tools
- Tally
- Snapshot
- Boardroom
- DeepDAO

## Conclusion

DAO governance requires careful design of voting mechanisms, security measures, and participation incentives. Build systems that enable effective decentralized decision-making while protecting against governance attacks.
