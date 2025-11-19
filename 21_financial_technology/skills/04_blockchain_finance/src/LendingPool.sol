// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LendingPool - Simplified Lending Protocol
 * @dev Allows users to deposit tokens and earn interest, borrow against collateral
 */
contract LendingPool is ReentrancyGuard, Pausable, Ownable {
    IERC20 public lendingToken;
    IERC20 public collateralToken;

    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    mapping(address => uint256) public collateral;

    uint256 public totalDeposits;
    uint256 public totalBorrows;
    
    uint256 public constant MAX_LTV = 75; // 75% max loan-to-value
    uint256 public constant INTEREST_RATE = 5; // 5% annual
    uint256 public constant LIQUIDATION_THRESHOLD = 80; // 80%

    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    event Borrow(address indexed user, uint256 amount);
    event Repay(address indexed user, uint256 amount);
    event Liquidation(address indexed borrower, address indexed liquidator);

    constructor(IERC20 _lendingToken, IERC20 _collateralToken) {
        lendingToken = _lendingToken;
        collateralToken = _collateralToken;
    }

    /**
     * @dev Deposit collateral
     */
    function depositCollateral(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        
        collateralToken.transferFrom(msg.sender, address(this), amount);
        collateral[msg.sender] += amount;
        
        emit Deposit(msg.sender, amount);
    }

    /**
     * @dev Supply liquidity
     */
    function supply(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        
        lendingToken.transferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
        totalDeposits += amount;
        
        emit Deposit(msg.sender, amount);
    }

    /**
     * @dev Withdraw supply with accrued interest
     */
    function withdraw(uint256 amount) external nonReentrant {
        require(deposits[msg.sender] >= amount, "Insufficient balance");
        require(lendingToken.balanceOf(address(this)) >= amount, "Insufficient liquidity");
        
        deposits[msg.sender] -= amount;
        totalDeposits -= amount;
        
        // Pay interest
        uint256 interest = calculateInterest(amount);
        lendingToken.transfer(msg.sender, amount + interest);
        
        emit Withdraw(msg.sender, amount);
    }

    /**
     * @dev Borrow against collateral
     */
    function borrow(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(lendingToken.balanceOf(address(this)) >= amount, "Insufficient liquidity");
        
        uint256 borrowLimit = getBorrowLimit(msg.sender);
        require(borrows[msg.sender] + amount <= borrowLimit, "Exceeds borrow limit");
        
        borrows[msg.sender] += amount;
        totalBorrows += amount;
        
        lendingToken.transfer(msg.sender, amount);
        emit Borrow(msg.sender, amount);
    }

    /**
     * @dev Repay borrow
     */
    function repay(uint256 amount) external nonReentrant {
        require(borrows[msg.sender] > 0, "No outstanding borrow");
        require(amount <= borrows[msg.sender], "Repay amount too high");
        
        lendingToken.transferFrom(msg.sender, address(this), amount);
        
        borrows[msg.sender] -= amount;
        totalBorrows -= amount;
        
        emit Repay(msg.sender, amount);
    }

    /**
     * @dev Calculate borrow limit based on collateral
     */
    function getBorrowLimit(address user) public view returns (uint256) {
        uint256 collateralValue = collateral[user]; // Assume 1:1 for simplicity
        return (collateralValue * MAX_LTV) / 100;
    }

    /**
     * @dev Calculate health factor
     */
    function getHealthFactor(address user) public view returns (uint256) {
        if (borrows[user] == 0) return type(uint256).max;
        
        uint256 collateralValue = collateral[user];
        return (collateralValue * 100) / borrows[user];
    }

    /**
     * @dev Liquidate undercollateralized position
     */
    function liquidate(address borrower) external nonReentrant whenNotPaused {
        uint256 healthFactor = getHealthFactor(borrower);
        require(healthFactor < LIQUIDATION_THRESHOLD, "Not liquidatable");
        
        uint256 seizedCollateral = collateral[borrower];
        uint256 borrowAmount = borrows[borrower];
        
        collateral[borrower] = 0;
        borrows[borrower] = 0;
        totalBorrows -= borrowAmount;
        
        collateralToken.transfer(msg.sender, seizedCollateral);
        
        emit Liquidation(borrower, msg.sender);
    }

    /**
     * @dev Calculate interest earned
     */
    function calculateInterest(uint256 amount) internal pure returns (uint256) {
        return (amount * INTEREST_RATE) / 100;
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Resume operations
     */
    function unpause() external onlyOwner {
        _unpause();
    }
}
