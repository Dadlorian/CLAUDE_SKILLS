// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract TokenVesting {
    IERC20 public token;
    address public beneficiary;
    uint256 public startTime;
    uint256 public duration = 365 days;
    uint256 public totalAmount;
    uint256 public releasedAmount;

    constructor(IERC20 _token, address _beneficiary, uint256 _totalAmount) {
        token = _token;
        beneficiary = _beneficiary;
        totalAmount = _totalAmount;
        startTime = block.timestamp;
    }

    function releasableAmount() public view returns (uint256) {
        uint256 elapsed = block.timestamp - startTime;
        if (elapsed >= duration) {
            return totalAmount - releasedAmount;
        }
        return (totalAmount * elapsed / duration) - releasedAmount;
    }

    function release() external {
        uint256 amount = releasableAmount();
        require(amount > 0, "Nothing to release");
        releasedAmount += amount;
        token.transfer(beneficiary, amount);
    }
}
