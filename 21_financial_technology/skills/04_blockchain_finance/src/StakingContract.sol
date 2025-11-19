// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title StakingContract - Earn rewards by staking tokens
 */
contract StakingContract is ReentrancyGuard {
    IERC20 public stakingToken;
    IERC20 public rewardToken;

    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public lastClaimTime;
    
    uint256 public totalStaked;
    uint256 public rewardRatePerDay = 1e18; // 1 token per day per staked unit

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor(IERC20 _stakingToken, IERC20 _rewardToken) {
        stakingToken = _stakingToken;
        rewardToken = _rewardToken;
    }

    /**
     * @dev Stake tokens
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        
        stakingToken.transferFrom(msg.sender, address(this), amount);
        
        // Claim any pending rewards first
        if (stakedBalance[msg.sender] > 0) {
            _claimRewards();
        }
        
        stakedBalance[msg.sender] += amount;
        totalStaked += amount;
        lastClaimTime[msg.sender] = block.timestamp;
        
        emit Staked(msg.sender, amount);
    }

    /**
     * @dev Unstake tokens
     */
    function unstake(uint256 amount) external nonReentrant {
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        
        // Claim rewards before unstaking
        _claimRewards();
        
        stakedBalance[msg.sender] -= amount;
        totalStaked -= amount;
        
        stakingToken.transfer(msg.sender, amount);
        
        emit Unstaked(msg.sender, amount);
    }

    /**
     * @dev Claim accumulated rewards
     */
    function claimRewards() external nonReentrant {
        require(stakedBalance[msg.sender] > 0, "No staked balance");
        _claimRewards();
    }

    /**
     * @dev Internal claim logic
     */
    function _claimRewards() internal {
        uint256 rewards = calculateRewards(msg.sender);
        require(rewards > 0, "No rewards to claim");
        
        rewardToken.transfer(msg.sender, rewards);
        lastClaimTime[msg.sender] = block.timestamp;
        
        emit RewardClaimed(msg.sender, rewards);
    }

    /**
     * @dev Calculate pending rewards
     */
    function calculateRewards(address user) public view returns (uint256) {
        if (stakedBalance[user] == 0) return 0;
        
        uint256 timeElapsed = block.timestamp - lastClaimTime[user];
        uint256 daysElapsed = timeElapsed / 1 days;
        
        return (stakedBalance[user] * rewardRatePerDay * daysElapsed) / 1e18;
    }

    /**
     * @dev Get staked balance
     */
    function getStakedBalance(address user) external view returns (uint256) {
        return stakedBalance[user];
    }

    /**
     * @dev Get total staked
     */
    function getTotalStaked() external view returns (uint256) {
        return totalStaked;
    }
}
