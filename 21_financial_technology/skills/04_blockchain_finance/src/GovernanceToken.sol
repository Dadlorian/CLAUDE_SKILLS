// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title GovernanceToken - DAO governance token with voting
 */
contract GovernanceToken is ERC20, Ownable {
    mapping(address => uint256) public votingPower;
    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;

    struct Proposal {
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 deadline;
        bool executed;
    }

    event ProposalCreated(uint256 indexed proposalId, string description);
    event Voted(uint256 indexed proposalId, address indexed voter, bool support);

    constructor() ERC20("Governance Token", "GOV") {
        _mint(msg.sender, 1_000_000 * 10 ** 18);
    }

    function createProposal(string memory description) external returns (uint256) {
        require(balanceOf(msg.sender) > 0, "Must hold tokens");
        
        proposals[proposalCount] = Proposal({
            description: description,
            forVotes: 0,
            againstVotes: 0,
            deadline: block.timestamp + 7 days,
            executed: false
        });

        emit ProposalCreated(proposalCount, description);
        return proposalCount++;
    }

    function vote(uint256 proposalId, bool support) external {
        require(block.timestamp < proposals[proposalId].deadline, "Proposal ended");
        uint256 balance = balanceOf(msg.sender);
        require(balance > 0, "Must hold tokens");

        if (support) {
            proposals[proposalId].forVotes += balance;
        } else {
            proposals[proposalId].againstVotes += balance;
        }

        emit Voted(proposalId, msg.sender, support);
    }

    function executeProposal(uint256 proposalId) external onlyOwner {
        Proposal storage proposal = proposals[proposalId];
        require(!proposal.executed, "Already executed");
        require(proposal.forVotes > proposal.againstVotes, "Proposal failed");

        proposal.executed = true;
    }
}
