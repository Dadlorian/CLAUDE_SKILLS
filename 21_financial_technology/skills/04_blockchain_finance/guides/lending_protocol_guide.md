# Lending Protocol Guide

## Architecture Overview

A lending protocol consists of:
1. **Pool Contract**: Manages deposits and borrows
2. **Interest Rate Model**: Calculates rates dynamically
3. **Oracle**: Provides collateral prices
4. **Risk Manager**: Liquidation and parameters

## Core Smart Contract

```solidity
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SimpleLendingPool is ReentrancyGuard {
    using SafeERC20 for IERC20;

    // State variables
    IERC20 public asset;
    IPriceOracle public priceOracle;

    mapping(address => uint256) public balances;
    mapping(address => uint256) public borrows;
    mapping(address => uint256) public collateral;

    uint256 public totalBorrowed;
    uint256 public constant MAX_LTV = 75; // 75% max LTV

    // Events
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    event Borrow(address indexed user, uint256 amount);
    event Repay(address indexed user, uint256 amount);
    event Liquidation(address indexed borrower, address liquidator, uint256 collateralSeized);

    constructor(IERC20 _asset, IPriceOracle _oracle) {
        asset = _asset;
        priceOracle = _oracle;
    }

    // Deposit collateral
    function depositCollateral(address collateralToken, uint256 amount) external {
        IERC20(collateralToken).safeTransferFrom(msg.sender, address(this), amount);
        collateral[msg.sender] += amount;
        emit Deposit(msg.sender, amount);
    }

    // Supply liquidity
    function supply(uint256 amount) external {
        asset.safeTransferFrom(msg.sender, address(this), amount);
        balances[msg.sender] += amount;
        emit Deposit(msg.sender, amount);
    }

    // Withdraw supply
    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        asset.safeTransfer(msg.sender, amount);
        emit Withdraw(msg.sender, amount);
    }

    // Borrow against collateral
    function borrow(uint256 amount) external nonReentrant {
        require(amount <= asset.balanceOf(address(this)), "Insufficient liquidity");

        // Check collateral
        uint256 borrowLimit = getBorrowLimit(msg.sender);
        uint256 currentBorrow = borrows[msg.sender] + amount;
        require(currentBorrow <= borrowLimit, "Exceeds borrow limit");

        borrows[msg.sender] += amount;
        totalBorrowed += amount;

        asset.safeTransfer(msg.sender, amount);
        emit Borrow(msg.sender, amount);
    }

    // Repay borrow
    function repay(uint256 amount) external nonReentrant {
        require(borrows[msg.sender] >= amount, "Repay amount too high");

        asset.safeTransferFrom(msg.sender, address(this), amount);

        borrows[msg.sender] -= amount;
        totalBorrowed -= amount;

        emit Repay(msg.sender, amount);
    }

    // Calculate borrow limit
    function getBorrowLimit(address user) public view returns (uint256) {
        uint256 collateralUSD = getCollateralValue(user);
        return (collateralUSD * MAX_LTV) / 100;
    }

    // Get collateral value in USD
    function getCollateralValue(address user) public view returns (uint256) {
        uint256 balance = collateral[user];
        uint256 price = priceOracle.getPrice();
        return (balance * price) / 1e18;
    }

    // Liquidation
    function liquidate(address borrower) external nonReentrant {
        uint256 borrowUSD = (borrows[borrower] * priceOracle.getPrice()) / 1e18;
        uint256 collateralUSD = getCollateralValue(borrower);

        // Calculate health factor
        require(collateralUSD < (borrowUSD * 100) / 80, "Not liquidatable");

        // Seize collateral
        uint256 seizedCollateral = collateral[borrower];
        collateral[borrower] = 0;
        borrows[borrower] = 0;
        totalBorrowed -= borrows[borrower];

        // Transfer to liquidator (with discount)
        IERC20(collateral[borrower]).safeTransfer(msg.sender, seizedCollateral);

        emit Liquidation(borrower, msg.sender, seizedCollateral);
    }

    // Get health factor
    function getHealthFactor(address user) external view returns (uint256) {
        if (borrows[user] == 0) return type(uint256).max;

        uint256 collateralValue = getCollateralValue(user);
        uint256 borrowValue = (borrows[user] * priceOracle.getPrice()) / 1e18;

        return (collateralValue * 100) / borrowValue;
    }
}
```

## Interest Rate Calculation

```solidity
contract InterestRateModel {
    uint256 constant BASE_RATE = 2e16; // 2%
    uint256 constant SLOPE1 = 4e16;    // 4%
    uint256 constant SLOPE2 = 75e16;   // 75%
    uint256 constant KINK = 80e16;     // 80% utilization

    function getInterestRate(uint256 supplied, uint256 borrowed) external pure returns (uint256) {
        if (supplied == 0) return BASE_RATE;

        uint256 utilization = (borrowed * 1e18) / supplied;

        if (utilization <= KINK) {
            return BASE_RATE + (utilization * SLOPE1) / 1e18;
        } else {
            uint256 excessUtil = utilization - KINK;
            return BASE_RATE + (KINK * SLOPE1) / 1e18 + (excessUtil * SLOPE2) / 1e18;
        }
    }
}
```

## Integration Test

```javascript
describe("Lending Pool", function() {
  it("Should execute full lending cycle", async function() {
    // 1. Deposit collateral
    await collateralToken.approve(pool.address, ethers.parseEther("100"));
    await pool.depositCollateral(collateralToken.address, ethers.parseEther("100"));

    // 2. Deposit liquidity
    await lendingToken.approve(pool.address, ethers.parseEther("1000"));
    await pool.supply(ethers.parseEther("1000"));

    // 3. Borrow
    const borrowAmount = ethers.parseEther("500");
    await pool.borrow(borrowAmount);

    // 4. Check borrow
    let borrowBalance = await pool.borrows(user.address);
    expect(borrowBalance).to.equal(borrowAmount);

    // 5. Repay
    await lendingToken.approve(pool.address, borrowAmount);
    await pool.repay(borrowAmount);

    // 6. Verify repaid
    borrowBalance = await pool.borrows(user.address);
    expect(borrowBalance).to.equal(0);
  });
});
```

## Deployment Checklist

- [ ] Interest rate model tested
- [ ] Liquidation mechanism working
- [ ] Oracle integration verified
- [ ] Risk parameters appropriate
- [ ] Emergency pause ready
- [ ] Insurance fund setup
- [ ] Monitoring active
- [ ] Documentation complete

---

**Key Takeaways**:
- Interest rates adjust with utilization
- Collateral provides borrow limit
- Liquidation prevents bad debt
- Health factor indicates position safety
- Proper risk parameters are critical
