// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LendingPool
 * @dev Simple lending pool with collateralized borrowing
 * Features:
 * - Supply assets and earn interest
 * - Borrow against collateral
 * - Liquidation mechanism
 * - Interest rate model
 * - Flash loans
 */
contract LendingPool is ReentrancyGuard, Ownable {
    struct Market {
        bool isListed;
        uint256 collateralFactor;      // Percentage in basis points (e.g., 7500 = 75%)
        uint256 reserveFactor;          // Percentage in basis points
        uint256 totalBorrows;
        uint256 totalReserves;
        uint256 totalCash;
        uint256 borrowIndex;
        uint256 lastUpdateTime;
        address aToken;
        mapping(address => uint256) accountBorrows;
        mapping(address => uint256) accountBorrowIndex;
    }

    // Constants
    uint256 public constant COLLATERAL_FACTOR_MAX = 9000; // 90%
    uint256 public constant LIQUIDATION_INCENTIVE = 10500; // 105% = 5% bonus
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public constant CLOSE_FACTOR = 5000; // 50% max liquidation

    // State variables
    mapping(address => Market) public markets;
    mapping(address => mapping(address => uint256)) public userCollateral;
    address[] public marketsList;

    // Interest rate model parameters
    uint256 public baseRatePerYear = 2e16;  // 2%
    uint256 public multiplierPerYear = 1e17; // 10%
    uint256 public jumpMultiplierPerYear = 5e17; // 50%
    uint256 public kink = 8e17; // 80%

    // Events
    event MarketListed(address indexed token, address indexed aToken);
    event Supply(address indexed user, address indexed token, uint256 amount);
    event Withdraw(address indexed user, address indexed token, uint256 amount);
    event Borrow(address indexed user, address indexed token, uint256 amount);
    event RepayBorrow(address indexed user, address indexed token, uint256 amount);
    event Liquidate(
        address indexed liquidator,
        address indexed borrower,
        address indexed tokenBorrowed,
        address tokenCollateral,
        uint256 repayAmount
    );

    constructor() Ownable(msg.sender) {}

    /**
     * @dev List a new market
     * @param token Underlying token address
     * @param collateralFactor Collateral factor in basis points
     */
    function listMarket(
        address token,
        uint256 collateralFactor,
        address aToken
    ) external onlyOwner {
        require(!markets[token].isListed, "Market already listed");
        require(collateralFactor <= COLLATERAL_FACTOR_MAX, "Invalid collateral factor");

        Market storage market = markets[token];
        market.isListed = true;
        market.collateralFactor = collateralFactor;
        market.reserveFactor = 1000; // 10%
        market.borrowIndex = 1e18;
        market.lastUpdateTime = block.timestamp;
        market.aToken = aToken;

        marketsList.push(token);

        emit MarketListed(token, aToken);
    }

    /**
     * @dev Supply assets to earn interest
     * @param token Token address
     * @param amount Amount to supply
     */
    function supply(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        require(market.isListed, "Market not listed");
        require(amount > 0, "Amount must be > 0");

        // Accrue interest
        _accrueInterest(token);

        // Transfer tokens from user
        IERC20(token).transferFrom(msg.sender, address(this), amount);

        // Mint aTokens
        uint256 aTokenAmount = amount; // Simplified: should use exchange rate
        AToken(market.aToken).mint(msg.sender, aTokenAmount);

        market.totalCash += amount;

        emit Supply(msg.sender, token, amount);
    }

    /**
     * @dev Withdraw supplied assets
     * @param token Token address
     * @param amount Amount to withdraw
     */
    function withdraw(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        require(market.isListed, "Market not listed");

        // Accrue interest
        _accrueInterest(token);

        // Burn aTokens
        uint256 aTokenAmount = amount; // Simplified: should use exchange rate
        AToken(market.aToken).burn(msg.sender, aTokenAmount);

        // Check if user has enough liquidity
        require(_checkLiquidity(msg.sender, token, amount, true), "Insufficient liquidity");

        // Transfer tokens to user
        IERC20(token).transfer(msg.sender, amount);
        market.totalCash -= amount;

        emit Withdraw(msg.sender, token, amount);
    }

    /**
     * @dev Borrow assets
     * @param token Token address
     * @param amount Amount to borrow
     */
    function borrow(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        require(market.isListed, "Market not listed");
        require(amount > 0 && amount <= market.totalCash, "Invalid amount");

        // Accrue interest
        _accrueInterest(token);

        // Check if user has enough collateral
        require(_checkBorrowAllowed(msg.sender, token, amount), "Insufficient collateral");

        // Update borrow balance
        uint256 accountBorrowsPrior = market.accountBorrows[msg.sender];
        uint256 accountBorrowsNew = accountBorrowsPrior + amount;

        market.accountBorrows[msg.sender] = accountBorrowsNew;
        market.accountBorrowIndex[msg.sender] = market.borrowIndex;
        market.totalBorrows += amount;
        market.totalCash -= amount;

        // Transfer tokens to user
        IERC20(token).transfer(msg.sender, amount);

        emit Borrow(msg.sender, token, amount);
    }

    /**
     * @dev Repay borrowed assets
     * @param token Token address
     * @param amount Amount to repay
     */
    function repayBorrow(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        require(market.isListed, "Market not listed");

        // Accrue interest
        _accrueInterest(token);

        uint256 accountBorrows = market.accountBorrows[msg.sender];
        uint256 repayAmount = amount > accountBorrows ? accountBorrows : amount;

        require(repayAmount > 0, "Nothing to repay");

        // Transfer tokens from user
        IERC20(token).transferFrom(msg.sender, address(this), repayAmount);

        // Update borrow balance
        market.accountBorrows[msg.sender] = accountBorrows - repayAmount;
        market.totalBorrows -= repayAmount;
        market.totalCash += repayAmount;

        emit RepayBorrow(msg.sender, token, repayAmount);
    }

    /**
     * @dev Liquidate undercollateralized position
     * @param borrower Borrower address
     * @param tokenBorrowed Token borrowed
     * @param tokenCollateral Token used as collateral
     * @param repayAmount Amount to repay
     */
    function liquidate(
        address borrower,
        address tokenBorrowed,
        address tokenCollateral,
        uint256 repayAmount
    ) external nonReentrant {
        require(borrower != msg.sender, "Cannot liquidate self");

        Market storage borrowMarket = markets[tokenBorrowed];
        Market storage collateralMarket = markets[tokenCollateral];

        require(borrowMarket.isListed && collateralMarket.isListed, "Market not listed");

        // Accrue interest
        _accrueInterest(tokenBorrowed);
        _accrueInterest(tokenCollateral);

        // Check if borrower is undercollateralized
        require(!_isHealthy(borrower), "Borrower is healthy");

        // Calculate max liquidation amount
        uint256 maxClose = (borrowMarket.accountBorrows[borrower] * CLOSE_FACTOR) / BASIS_POINTS;
        require(repayAmount <= maxClose, "Repay amount too high");

        // Calculate collateral to seize
        uint256 seizeTokens = (repayAmount * LIQUIDATION_INCENTIVE) / BASIS_POINTS;

        // Transfer repay amount from liquidator
        IERC20(tokenBorrowed).transferFrom(msg.sender, address(this), repayAmount);

        // Update borrow balance
        borrowMarket.accountBorrows[borrower] -= repayAmount;
        borrowMarket.totalBorrows -= repayAmount;
        borrowMarket.totalCash += repayAmount;

        // Transfer collateral to liquidator
        AToken(collateralMarket.aToken).transferFrom(borrower, msg.sender, seizeTokens);

        emit Liquidate(msg.sender, borrower, tokenBorrowed, tokenCollateral, repayAmount);
    }

    /**
     * @dev Flash loan function
     * @param token Token to borrow
     * @param amount Amount to borrow
     * @param data Callback data
     */
    function flashLoan(
        address token,
        uint256 amount,
        bytes calldata data
    ) external nonReentrant {
        Market storage market = markets[token];
        require(market.isListed, "Market not listed");
        require(amount <= market.totalCash, "Insufficient liquidity");

        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        uint256 fee = (amount * 9) / 10000; // 0.09% fee

        // Transfer tokens to borrower
        IERC20(token).transfer(msg.sender, amount);

        // Execute callback
        IFlashLoanReceiver(msg.sender).executeOperation(token, amount, fee, data);

        // Check repayment
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        require(balanceAfter >= balanceBefore + fee, "Flash loan not repaid");

        market.totalReserves += fee;
    }

    /**
     * @dev Get account liquidity
     * @param account User address
     * @return liquidity Available liquidity
     * @return shortfall Shortfall amount
     */
    function getAccountLiquidity(address account)
        public
        view
        returns (uint256 liquidity, uint256 shortfall)
    {
        uint256 sumCollateral;
        uint256 sumBorrow;

        for (uint256 i = 0; i < marketsList.length; i++) {
            address token = marketsList[i];
            Market storage market = markets[token];

            // Calculate collateral value
            uint256 aTokenBalance = AToken(market.aToken).balanceOf(account);
            if (aTokenBalance > 0) {
                uint256 collateralValue = (aTokenBalance * market.collateralFactor) / BASIS_POINTS;
                sumCollateral += collateralValue;
            }

            // Calculate borrow value
            uint256 borrowBalance = market.accountBorrows[account];
            if (borrowBalance > 0) {
                sumBorrow += borrowBalance;
            }
        }

        if (sumCollateral > sumBorrow) {
            liquidity = sumCollateral - sumBorrow;
            shortfall = 0;
        } else {
            liquidity = 0;
            shortfall = sumBorrow - sumCollateral;
        }
    }

    /**
     * @dev Internal function to accrue interest
     */
    function _accrueInterest(address token) internal {
        Market storage market = markets[token];

        uint256 currentTime = block.timestamp;
        uint256 timeElapsed = currentTime - market.lastUpdateTime;

        if (timeElapsed == 0) return;

        uint256 cashPrior = market.totalCash;
        uint256 borrowsPrior = market.totalBorrows;
        uint256 reservesPrior = market.totalReserves;

        uint256 borrowRate = _getBorrowRate(cashPrior, borrowsPrior, reservesPrior);
        uint256 interestAccumulated = (borrowsPrior * borrowRate * timeElapsed) / 1e18;
        uint256 totalBorrowsNew = borrowsPrior + interestAccumulated;
        uint256 totalReservesNew = reservesPrior +
            (interestAccumulated * market.reserveFactor) / BASIS_POINTS;

        market.borrowIndex = market.borrowIndex +
            (market.borrowIndex * borrowRate * timeElapsed) / 1e18;
        market.totalBorrows = totalBorrowsNew;
        market.totalReserves = totalReservesNew;
        market.lastUpdateTime = currentTime;
    }

    /**
     * @dev Calculate borrow rate based on utilization
     */
    function _getBorrowRate(
        uint256 cash,
        uint256 borrows,
        uint256 reserves
    ) internal view returns (uint256) {
        if (borrows == 0) return baseRatePerYear;

        uint256 utilization = (borrows * 1e18) / (cash + borrows - reserves);

        if (utilization <= kink) {
            return baseRatePerYear + (multiplierPerYear * utilization) / 1e18;
        } else {
            uint256 normalRate = baseRatePerYear + (multiplierPerYear * kink) / 1e18;
            uint256 excessUtil = utilization - kink;
            return normalRate + (jumpMultiplierPerYear * excessUtil) / 1e18;
        }
    }

    /**
     * @dev Check if user is healthy (not liquidatable)
     */
    function _isHealthy(address account) internal view returns (bool) {
        (uint256 liquidity, uint256 shortfall) = getAccountLiquidity(account);
        return shortfall == 0;
    }

    /**
     * @dev Check if borrow is allowed
     */
    function _checkBorrowAllowed(
        address account,
        address token,
        uint256 amount
    ) internal view returns (bool) {
        (uint256 liquidity, ) = getAccountLiquidity(account);
        return liquidity >= amount;
    }

    /**
     * @dev Check if withdrawal is allowed
     */
    function _checkLiquidity(
        address account,
        address token,
        uint256 amount,
        bool isWithdraw
    ) internal view returns (bool) {
        (uint256 liquidity, ) = getAccountLiquidity(account);
        if (!isWithdraw) return true;

        Market storage market = markets[token];
        uint256 collateralValue = (amount * market.collateralFactor) / BASIS_POINTS;

        return liquidity >= collateralValue;
    }
}

/**
 * @title AToken
 * @dev Interest-bearing token representing supplied assets
 */
contract AToken is ERC20 {
    address public pool;

    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        pool = msg.sender;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == pool, "Only pool");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == pool, "Only pool");
        _burn(from, amount);
    }
}

/**
 * @title IFlashLoanReceiver
 * @dev Interface for flash loan receivers
 */
interface IFlashLoanReceiver {
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external;
}
