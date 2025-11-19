// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract CollateralManager {
    mapping(address => mapping(address => uint256)) public collateral;
    mapping(address => uint256) public borrowings;

    event CollateralDeposited(address indexed user, address indexed token, uint256 amount);
    event CollateralWithdrawn(address indexed user, address indexed token, uint256 amount);

    function depositCollateral(address token, uint256 amount) external {
        IERC20(token).transferFrom(msg.sender, address(this), amount);
        collateral[msg.sender][token] += amount;
        emit CollateralDeposited(msg.sender, token, amount);
    }

    function withdrawCollateral(address token, uint256 amount) external {
        require(collateral[msg.sender][token] >= amount);
        collateral[msg.sender][token] -= amount;
        IERC20(token).transfer(msg.sender, amount);
        emit CollateralWithdrawn(msg.sender, token, amount);
    }

    function getCollateralValue(address user, address token) external view returns (uint256) {
        return collateral[user][token];
    }
}
