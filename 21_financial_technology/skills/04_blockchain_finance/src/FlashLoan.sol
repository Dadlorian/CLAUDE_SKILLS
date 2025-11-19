// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanReceiverBase.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IFlashLoanReceiver {
    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params) external returns (bytes32);
}

/**
 * @title FlashLoanExample - Flash loan arbitrage example
 */
contract FlashLoanExample {
    address public lender;
    
    event FlashLoanExecuted(address asset, uint256 amount, uint256 premium);

    constructor(address _lender) {
        lender = _lender;
    }

    /**
     * @dev Initiate flash loan
     */
    function executeFlashLoan(address asset, uint256 amount) external {
        // In real implementation, call actual lending pool
        // This is simplified for demonstration
        
        uint256 premium = (amount * 9) / 10000; // 0.09% fee
        
        // Transfer borrowed amount
        IERC20(asset).transferFrom(lender, address(this), amount);
        
        // Execute operations (arbitrage, liquidation, etc)
        _executeOperations(asset, amount);
        
        // Repay with premium
        uint256 amountOwed = amount + premium;
        IERC20(asset).approve(lender, amountOwed);
        IERC20(asset).transferFrom(address(this), lender, amountOwed);
        
        emit FlashLoanExecuted(asset, amount, premium);
    }

    /**
     * @dev Execute trading operations
     */
    function _executeOperations(address asset, uint256 amount) internal {
        // Custom arbitrage or liquidation logic
        // For example:
        // 1. Swap on DEX A
        // 2. Swap on DEX B
        // 3. Pocket the difference
    }
}
