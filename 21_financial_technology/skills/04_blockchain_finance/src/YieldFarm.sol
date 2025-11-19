// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract YieldFarm {
    IERC20 public farmToken;
    IERC20 public rewardToken;

    mapping(address => uint256) public deposits;
    uint256 public totalDeposits;
    uint256 public rewardPerTokenPerDay = 1e18;

    function deposit(uint256 amount) external {
        farmToken.transferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
        totalDeposits += amount;
    }

    function withdraw(uint256 amount) external {
        require(deposits[msg.sender] >= amount);
        deposits[msg.sender] -= amount;
        totalDeposits -= amount;
        farmToken.transfer(msg.sender, amount);
    }

    function harvestRewards() external {
        uint256 rewards = (deposits[msg.sender] * rewardPerTokenPerDay) / 1e18;
        rewardToken.transfer(msg.sender, rewards);
    }
}
