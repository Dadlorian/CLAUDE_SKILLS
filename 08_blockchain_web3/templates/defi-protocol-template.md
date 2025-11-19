# DeFi Protocol Development Template

This template provides a comprehensive framework for building production-ready DeFi protocols with security, efficiency, and best practices.

## AMM (Automated Market Maker) Template

### Core AMM Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SimpleDEX
 * @notice Constant product AMM (x * y = k) similar to Uniswap V2
 * @dev Implements:
 * - Liquidity provision and removal
 * - Token swapping with 0.3% fee
 * - TWAP oracle
 * - Flash swap protection
 * - MEV mitigation through slippage
 */
contract SimpleDEX is ERC20, ReentrancyGuard, Ownable {
    IERC20 public immutable token0;
    IERC20 public immutable token1;

    uint112 private reserve0;
    uint112 private reserve1;
    uint32 private blockTimestampLast;

    uint256 public price0CumulativeLast;
    uint256 public price1CumulativeLast;
    uint256 public kLast;

    uint256 private constant MINIMUM_LIQUIDITY = 10**3;
    uint256 private constant FEE_DENOMINATOR = 1000;
    uint256 private constant FEE_NUMERATOR = 3; // 0.3% fee

    event Mint(address indexed sender, uint256 amount0, uint256 amount1);
    event Burn(address indexed sender, uint256 amount0, uint256 amount1, address indexed to);
    event Swap(
        address indexed sender,
        uint256 amount0In,
        uint256 amount1In,
        uint256 amount0Out,
        uint256 amount1Out,
        address indexed to
    );
    event Sync(uint112 reserve0, uint112 reserve1);

    error InsufficientInputAmount();
    error InsufficientOutputAmount();
    error InsufficientLiquidity();
    error InvalidTo();
    error InvalidK();
    error Overflow();

    constructor(address _token0, address _token1) ERC20("LP Token", "LP") {
        token0 = IERC20(_token0);
        token1 = IERC20(_token1);
    }

    /**
     * @notice Add liquidity to the pool
     * @param amount0Desired Desired amount of token0
     * @param amount1Desired Desired amount of token1
     * @param amount0Min Minimum amount of token0
     * @param amount1Min Minimum amount of token1
     * @param to Recipient of LP tokens
     * @param deadline Transaction deadline
     * @return amount0 Actual amount of token0 added
     * @return amount1 Actual amount of token1 added
     * @return liquidity LP tokens minted
     */
    function addLiquidity(
        uint256 amount0Desired,
        uint256 amount1Desired,
        uint256 amount0Min,
        uint256 amount1Min,
        address to,
        uint256 deadline
    ) external nonReentrant returns (uint256 amount0, uint256 amount1, uint256 liquidity) {
        require(block.timestamp <= deadline, "Deadline expired");

        (uint112 _reserve0, uint112 _reserve1, ) = getReserves();

        if (_reserve0 == 0 && _reserve1 == 0) {
            // Initial liquidity
            (amount0, amount1) = (amount0Desired, amount1Desired);
        } else {
            // Calculate optimal amounts maintaining ratio
            uint256 amount1Optimal = quote(amount0Desired, _reserve0, _reserve1);
            if (amount1Optimal <= amount1Desired) {
                require(amount1Optimal >= amount1Min, "Insufficient amount1");
                (amount0, amount1) = (amount0Desired, amount1Optimal);
            } else {
                uint256 amount0Optimal = quote(amount1Desired, _reserve1, _reserve0);
                require(amount0Optimal <= amount0Desired && amount0Optimal >= amount0Min, "Insufficient amount0");
                (amount0, amount1) = (amount0Optimal, amount1Desired);
            }
        }

        // Transfer tokens
        token0.transferFrom(msg.sender, address(this), amount0);
        token1.transferFrom(msg.sender, address(this), amount1);

        // Mint LP tokens
        liquidity = _mint(to);

        emit Mint(msg.sender, amount0, amount1);
    }

    /**
     * @notice Remove liquidity from the pool
     * @param liquidity Amount of LP tokens to burn
     * @param amount0Min Minimum amount of token0 to receive
     * @param amount1Min Minimum amount of token1 to receive
     * @param to Recipient of tokens
     * @param deadline Transaction deadline
     * @return amount0 Amount of token0 received
     * @return amount1 Amount of token1 received
     */
    function removeLiquidity(
        uint256 liquidity,
        uint256 amount0Min,
        uint256 amount1Min,
        address to,
        uint256 deadline
    ) external nonReentrant returns (uint256 amount0, uint256 amount1) {
        require(block.timestamp <= deadline, "Deadline expired");

        // Burn LP tokens
        _transfer(msg.sender, address(this), liquidity);
        (amount0, amount1) = _burn(to);

        require(amount0 >= amount0Min, "Insufficient amount0");
        require(amount1 >= amount1Min, "Insufficient amount1");

        emit Burn(msg.sender, amount0, amount1, to);
    }

    /**
     * @notice Swap tokens
     * @param amount0Out Desired amount of token0 out
     * @param amount1Out Desired amount of token1 out
     * @param to Recipient address
     * @param minAmountOut Minimum amount out for slippage protection
     */
    function swap(
        uint256 amount0Out,
        uint256 amount1Out,
        address to,
        uint256 minAmountOut
    ) external nonReentrant {
        if (amount0Out == 0 && amount1Out == 0) revert InsufficientOutputAmount();
        if (to == address(token0) || to == address(token1)) revert InvalidTo();

        (uint112 _reserve0, uint112 _reserve1, ) = getReserves();
        if (amount0Out >= _reserve0 || amount1Out >= _reserve1) revert InsufficientLiquidity();

        // Optimistic transfer
        if (amount0Out > 0) token0.transfer(to, amount0Out);
        if (amount1Out > 0) token1.transfer(to, amount1Out);

        // Calculate input amounts
        uint256 balance0 = token0.balanceOf(address(this));
        uint256 balance1 = token1.balanceOf(address(this));

        uint256 amount0In = balance0 > _reserve0 - amount0Out ? balance0 - (_reserve0 - amount0Out) : 0;
        uint256 amount1In = balance1 > _reserve1 - amount1Out ? balance1 - (_reserve1 - amount1Out) : 0;

        if (amount0In == 0 && amount1In == 0) revert InsufficientInputAmount();

        // Verify K (with fee)
        {
            uint256 balance0Adjusted = (balance0 * 1000) - (amount0In * FEE_NUMERATOR);
            uint256 balance1Adjusted = (balance1 * 1000) - (amount1In * FEE_NUMERATOR);
            if (balance0Adjusted * balance1Adjusted < uint256(_reserve0) * uint256(_reserve1) * (1000**2)) {
                revert InvalidK();
            }
        }

        // Slippage check
        uint256 amountOut = amount0Out > 0 ? amount0Out : amount1Out;
        require(amountOut >= minAmountOut, "Slippage exceeded");

        _update(balance0, balance1, _reserve0, _reserve1);
        emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);
    }

    /**
     * @notice Get output amount for a given input
     * @param amountIn Input amount
     * @param reserveIn Input token reserve
     * @param reserveOut Output token reserve
     * @return amountOut Output amount after fees
     */
    function getAmountOut(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut
    ) public pure returns (uint256 amountOut) {
        if (amountIn == 0) revert InsufficientInputAmount();
        if (reserveIn == 0 || reserveOut == 0) revert InsufficientLiquidity();

        uint256 amountInWithFee = amountIn * (FEE_DENOMINATOR - FEE_NUMERATOR);
        uint256 numerator = amountInWithFee * reserveOut;
        uint256 denominator = (reserveIn * FEE_DENOMINATOR) + amountInWithFee;
        amountOut = numerator / denominator;
    }

    /**
     * @notice Get input amount needed for desired output
     * @param amountOut Desired output amount
     * @param reserveIn Input token reserve
     * @param reserveOut Output token reserve
     * @return amountIn Required input amount
     */
    function getAmountIn(
        uint256 amountOut,
        uint256 reserveIn,
        uint256 reserveOut
    ) public pure returns (uint256 amountIn) {
        if (amountOut == 0) revert InsufficientOutputAmount();
        if (reserveIn == 0 || reserveOut == 0) revert InsufficientLiquidity();

        uint256 numerator = reserveIn * amountOut * FEE_DENOMINATOR;
        uint256 denominator = (reserveOut - amountOut) * (FEE_DENOMINATOR - FEE_NUMERATOR);
        amountIn = (numerator / denominator) + 1;
    }

    /**
     * @notice Get current reserves
     * @return _reserve0 Token0 reserve
     * @return _reserve1 Token1 reserve
     * @return _blockTimestampLast Last update timestamp
     */
    function getReserves() public view returns (uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast) {
        _reserve0 = reserve0;
        _reserve1 = reserve1;
        _blockTimestampLast = blockTimestampLast;
    }

    /**
     * @notice Quote amount based on reserves
     */
    function quote(uint256 amountA, uint256 reserveA, uint256 reserveB) internal pure returns (uint256 amountB) {
        require(amountA > 0, "Insufficient amount");
        require(reserveA > 0 && reserveB > 0, "Insufficient liquidity");
        amountB = (amountA * reserveB) / reserveA;
    }

    /**
     * @dev Mint LP tokens
     */
    function _mint(address to) private returns (uint256 liquidity) {
        (uint112 _reserve0, uint112 _reserve1, ) = getReserves();
        uint256 balance0 = token0.balanceOf(address(this));
        uint256 balance1 = token1.balanceOf(address(this));
        uint256 amount0 = balance0 - _reserve0;
        uint256 amount1 = balance1 - _reserve1;

        uint256 _totalSupply = totalSupply();
        if (_totalSupply == 0) {
            liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(address(1), MINIMUM_LIQUIDITY); // Permanently lock minimum liquidity
        } else {
            liquidity = min((amount0 * _totalSupply) / _reserve0, (amount1 * _totalSupply) / _reserve1);
        }

        if (liquidity == 0) revert InsufficientLiquidity();
        _mint(to, liquidity);

        _update(balance0, balance1, _reserve0, _reserve1);
    }

    /**
     * @dev Burn LP tokens
     */
    function _burn(address to) private returns (uint256 amount0, uint256 amount1) {
        (uint112 _reserve0, uint112 _reserve1, ) = getReserves();
        uint256 balance0 = token0.balanceOf(address(this));
        uint256 balance1 = token1.balanceOf(address(this));
        uint256 liquidity = balanceOf(address(this));

        uint256 _totalSupply = totalSupply();
        amount0 = (liquidity * balance0) / _totalSupply;
        amount1 = (liquidity * balance1) / _totalSupply;

        if (amount0 == 0 || amount1 == 0) revert InsufficientLiquidity();

        _burn(address(this), liquidity);
        token0.transfer(to, amount0);
        token1.transfer(to, amount1);

        balance0 = token0.balanceOf(address(this));
        balance1 = token1.balanceOf(address(this));

        _update(balance0, balance1, _reserve0, _reserve1);
    }

    /**
     * @dev Update reserves and price accumulators
     */
    function _update(uint256 balance0, uint256 balance1, uint112 _reserve0, uint112 _reserve1) private {
        if (balance0 > type(uint112).max || balance1 > type(uint112).max) revert Overflow();

        uint32 blockTimestamp = uint32(block.timestamp % 2**32);
        unchecked {
            uint32 timeElapsed = blockTimestamp - blockTimestampLast;
            if (timeElapsed > 0 && _reserve0 != 0 && _reserve1 != 0) {
                // TWAP oracle update
                price0CumulativeLast += uint256(_reserve1) * timeElapsed / uint256(_reserve0);
                price1CumulativeLast += uint256(_reserve0) * timeElapsed / uint256(_reserve1);
            }
        }

        reserve0 = uint112(balance0);
        reserve1 = uint112(balance1);
        blockTimestampLast = blockTimestamp;
        emit Sync(reserve0, reserve1);
    }

    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }

    function min(uint256 x, uint256 y) internal pure returns (uint256 z) {
        z = x < y ? x : y;
    }
}
```

## Lending Protocol Template

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LendingPool
 * @notice Aave/Compound-style lending and borrowing
 * @dev Features:
 * - Interest accrual
 * - Collateralized borrowing
 * - Liquidations
 * - Variable interest rates
 */
contract LendingPool is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    struct Market {
        bool isListed;
        uint256 totalSupply;
        uint256 totalBorrows;
        uint256 collateralFactor; // 1e18 = 100%
        uint256 reserveFactor;     // 1e18 = 100%
        uint256 borrowIndex;
        uint256 supplyIndex;
        uint256 accrualBlockNumber;
        mapping(address => uint256) accountSupply;
        mapping(address => uint256) accountBorrows;
        mapping(address => uint256) borrowIndexSnapshot;
    }

    mapping(address => Market) public markets;
    mapping(address => address[]) public accountAssets;

    uint256 private constant MANTISSA = 1e18;
    uint256 private constant BLOCKS_PER_YEAR = 2_102_400; // ~15s blocks

    // Interest rate model parameters
    uint256 public baseRatePerBlock = 0;
    uint256 public multiplierPerBlock = 23782343987; // ~5% APR at 100% utilization
    uint256 public jumpMultiplierPerBlock = 518455098934; // Jump to ~109% APR above kink
    uint256 public kink = 0.8e18; // 80% utilization

    event Supply(address indexed user, address indexed token, uint256 amount);
    event Withdraw(address indexed user, address indexed token, uint256 amount);
    event Borrow(address indexed user, address indexed token, uint256 amount);
    event RepayBorrow(address indexed user, address indexed token, uint256 amount);
    event Liquidate(
        address indexed liquidator,
        address indexed borrower,
        address indexed collateralToken,
        address borrowToken,
        uint256 repayAmount,
        uint256 seizedAmount
    );

    error MarketNotListed();
    error InsufficientCollateral();
    error InsufficientLiquidity();
    error BorrowCapExceeded();
    error LiquidationNotAllowed();

    /**
     * @notice Supply tokens to earn interest
     * @param token Token address
     * @param amount Amount to supply
     */
    function supply(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        if (!market.isListed) revert MarketNotListed();

        accrueInterest(token);

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        uint256 supplyAmount = (amount * MANTISSA) / market.supplyIndex;
        market.accountSupply[msg.sender] += supplyAmount;
        market.totalSupply += supplyAmount;

        // Add to user's asset list if first time
        _addToAccountAssets(msg.sender, token);

        emit Supply(msg.sender, token, amount);
    }

    /**
     * @notice Withdraw supplied tokens
     * @param token Token address
     * @param amount Amount to withdraw
     */
    function withdraw(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        if (!market.isListed) revert MarketNotListed();

        accrueInterest(token);

        uint256 supplyAmount = (amount * MANTISSA) / market.supplyIndex;
        require(market.accountSupply[msg.sender] >= supplyAmount, "Insufficient supply");

        market.accountSupply[msg.sender] -= supplyAmount;
        market.totalSupply -= supplyAmount;

        // Check if withdrawal would put account underwater
        require(_isHealthy(msg.sender), "Insufficient collateral");

        IERC20(token).safeTransfer(msg.sender, amount);

        emit Withdraw(msg.sender, token, amount);
    }

    /**
     * @notice Borrow tokens against collateral
     * @param token Token address
     * @param amount Amount to borrow
     */
    function borrow(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        if (!market.isListed) revert MarketNotListed();

        accrueInterest(token);

        // Check available liquidity
        uint256 cash = IERC20(token).balanceOf(address(this));
        if (cash < amount) revert InsufficientLiquidity();

        uint256 borrowAmount = (amount * MANTISSA) / market.borrowIndex;
        market.accountBorrows[msg.sender] += borrowAmount;
        market.borrowIndexSnapshot[msg.sender] = market.borrowIndex;
        market.totalBorrows += borrowAmount;

        // Check if borrow would put account underwater
        if (!_isHealthy(msg.sender)) revert InsufficientCollateral();

        IERC20(token).safeTransfer(msg.sender, amount);

        emit Borrow(msg.sender, token, amount);
    }

    /**
     * @notice Repay borrowed tokens
     * @param token Token address
     * @param amount Amount to repay
     */
    function repayBorrow(address token, uint256 amount) external nonReentrant {
        Market storage market = markets[token];
        if (!market.isListed) revert MarketNotListed();

        accrueInterest(token);

        uint256 borrowBalance = _getBorrowBalance(msg.sender, token);
        uint256 repayAmount = amount > borrowBalance ? borrowBalance : amount;

        IERC20(token).safeTransferFrom(msg.sender, address(this), repayAmount);

        uint256 borrowAmountToReduce = (repayAmount * MANTISSA) / market.borrowIndex;
        market.accountBorrows[msg.sender] -= borrowAmountToReduce;
        market.totalBorrows -= borrowAmountToReduce;

        emit RepayBorrow(msg.sender, token, repayAmount);
    }

    /**
     * @notice Liquidate underwater position
     * @param borrower Address of borrower
     * @param borrowToken Token borrowed
     * @param collateralToken Token to seize
     * @param repayAmount Amount to repay
     */
    function liquidate(
        address borrower,
        address borrowToken,
        address collateralToken,
        uint256 repayAmount
    ) external nonReentrant {
        accrueInterest(borrowToken);
        accrueInterest(collateralToken);

        // Check if borrower is underwater
        if (_isHealthy(borrower)) revert LiquidationNotAllowed();

        // Repay borrow
        IERC20(borrowToken).safeTransferFrom(msg.sender, address(this), repayAmount);

        Market storage borrowMarket = markets[borrowToken];
        uint256 borrowAmountToReduce = (repayAmount * MANTISSA) / borrowMarket.borrowIndex;
        borrowMarket.accountBorrows[borrower] -= borrowAmountToReduce;
        borrowMarket.totalBorrows -= borrowAmountToReduce;

        // Seize collateral (with liquidation incentive)
        uint256 seizeAmount = _calculateSeizeAmount(borrowToken, collateralToken, repayAmount);

        Market storage collateralMarket = markets[collateralToken];
        uint256 seizeSupply = (seizeAmount * MANTISSA) / collateralMarket.supplyIndex;

        collateralMarket.accountSupply[borrower] -= seizeSupply;
        collateralMarket.accountSupply[msg.sender] += seizeSupply;

        emit Liquidate(msg.sender, borrower, collateralToken, borrowToken, repayAmount, seizeAmount);
    }

    /**
     * @notice Accrue interest
     * @param token Token address
     */
    function accrueInterest(address token) public {
        Market storage market = markets[token];

        uint256 currentBlock = block.number;
        if (market.accrualBlockNumber == currentBlock) return;

        uint256 cash = IERC20(token).balanceOf(address(this));
        uint256 borrows = (market.totalBorrows * market.borrowIndex) / MANTISSA;
        uint256 reserves = 0; // Simplified

        if (borrows == 0) {
            market.accrualBlockNumber = currentBlock;
            return;
        }

        // Calculate interest rate
        uint256 utilizationRate = (borrows * MANTISSA) / (cash + borrows - reserves);
        uint256 borrowRate = _getBorrowRate(utilizationRate);

        uint256 blocksDelta = currentBlock - market.accrualBlockNumber;
        uint256 interestFactor = borrowRate * blocksDelta;

        // Update indices
        market.borrowIndex = (market.borrowIndex * (MANTISSA + interestFactor)) / MANTISSA;
        market.supplyIndex = (market.supplyIndex * (MANTISSA + (interestFactor * (MANTISSA - market.reserveFactor)) / MANTISSA)) / MANTISSA;
        market.accrualBlockNumber = currentBlock;
    }

    /**
     * @dev Check if account is healthy (collateral > borrows)
     */
    function _isHealthy(address account) internal view returns (bool) {
        (uint256 collateralValue, uint256 borrowValue) = _getAccountLiquidity(account);
        return collateralValue >= borrowValue;
    }

    /**
     * @dev Get account liquidity
     */
    function _getAccountLiquidity(address account) internal view returns (uint256 collateral, uint256 borrows) {
        address[] memory assets = accountAssets[account];

        for (uint256 i = 0; i < assets.length; i++) {
            address token = assets[i];
            Market storage market = markets[token];

            uint256 supplyBalance = (market.accountSupply[account] * market.supplyIndex) / MANTISSA;
            uint256 borrowBalance = _getBorrowBalance(account, token);

            // Simplified: assume 1:1 USD price for all tokens
            // In production, use oracle prices
            collateral += (supplyBalance * market.collateralFactor) / MANTISSA;
            borrows += borrowBalance;
        }
    }

    /**
     * @dev Get borrow balance with interest
     */
    function _getBorrowBalance(address account, address token) internal view returns (uint256) {
        Market storage market = markets[token];
        uint256 borrowAmount = market.accountBorrows[account];
        if (borrowAmount == 0) return 0;

        return (borrowAmount * market.borrowIndex) / MANTISSA;
    }

    /**
     * @dev Calculate borrow rate based on utilization
     */
    function _getBorrowRate(uint256 utilizationRate) internal view returns (uint256) {
        if (utilizationRate <= kink) {
            return baseRatePerBlock + (multiplierPerBlock * utilizationRate) / MANTISSA;
        } else {
            uint256 normalRate = baseRatePerBlock + (multiplierPerBlock * kink) / MANTISSA;
            uint256 excessUtil = utilizationRate - kink;
            return normalRate + (jumpMultiplierPerBlock * excessUtil) / MANTISSA;
        }
    }

    /**
     * @dev Calculate amount to seize in liquidation
     */
    function _calculateSeizeAmount(
        address borrowToken,
        address collateralToken,
        uint256 repayAmount
    ) internal view returns (uint256) {
        // Simplified: 10% liquidation incentive
        // In production, use oracle prices
        return (repayAmount * 110) / 100;
    }

    /**
     * @dev Add asset to account's asset list
     */
    function _addToAccountAssets(address account, address token) internal {
        address[] storage assets = accountAssets[account];
        for (uint256 i = 0; i < assets.length; i++) {
            if (assets[i] == token) return;
        }
        assets.push(token);
    }

    /**
     * @notice Add market (admin only)
     */
    function addMarket(address token, uint256 collateralFactor) external onlyOwner {
        markets[token].isListed = true;
        markets[token].collateralFactor = collateralFactor;
        markets[token].reserveFactor = 0.1e18; // 10%
        markets[token].borrowIndex = MANTISSA;
        markets[token].supplyIndex = MANTISSA;
        markets[token].accrualBlockNumber = block.number;
    }
}
```

## Testing DeFi Protocols

```solidity
// test/DeFiProtocol.t.sol
contract SimpleDEXTest is Test {
    SimpleDEX public dex;
    MockERC20 public token0;
    MockERC20 public token1;

    address alice = makeAddr("alice");
    address bob = makeAddr("bob");

    function setUp() public {
        token0 = new MockERC20("Token0", "TK0", 18);
        token1 = new MockERC20("Token1", "TK1", 18);
        dex = new SimpleDEX(address(token0), address(token1));

        // Mint tokens
        token0.mint(alice, 1000 ether);
        token1.mint(alice, 1000 ether);
        token0.mint(bob, 1000 ether);
        token1.mint(bob, 1000 ether);
    }

    function test_AddInitialLiquidity() public {
        vm.startPrank(alice);
        token0.approve(address(dex), 100 ether);
        token1.approve(address(dex), 100 ether);

        (uint256 amount0, uint256 amount1, uint256 liquidity) = dex.addLiquidity(
            100 ether,
            100 ether,
            100 ether,
            100 ether,
            alice,
            block.timestamp + 1 hours
        );

        assertEq(amount0, 100 ether);
        assertEq(amount1, 100 ether);
        assertGt(liquidity, 0);
        vm.stopPrank();
    }

    function testFuzz_Swap(uint96 amountIn) public {
        vm.assume(amountIn > 1000 && amountIn < 10 ether);

        // Add liquidity first
        test_AddInitialLiquidity();

        vm.startPrank(bob);
        token0.approve(address(dex), amountIn);

        uint256 amountOut = dex.getAmountOut(amountIn, 100 ether, 100 ether);

        dex.swap(0, amountOut, bob, amountOut * 99 / 100); // 1% slippage
        vm.stopPrank();
    }

    function test_RevertWhen_InsufficientLiquidity() public {
        vm.expectRevert(SimpleDEX.InsufficientLiquidity.selector);
        dex.swap(0, 1 ether, alice, 0);
    }
}
```

## Security Considerations

### Flash Loan Protection
- Implement proper K validation
- Use re-entrancy guards
- Consider TWAPoracle minimums

### Oracle Manipulation
- Use Chainlink price feeds
- Implement TWAP fallbacks
- Validate price bounds

### MEV Protection
- Slippage limits
- Transaction deadlines
- Commit-reveal patterns

### Economic Attacks
- Monitor large transactions
- Implement circuit breakers
- Cap borrowing limits

## Deployment Checklist

- [ ] All economic parameters audited
- [ ] Oracle integration tested
- [ ] Flash loan attack scenarios tested
- [ ] Fork tests against mainnet
- [ ] Gas optimization complete
- [ ] External security audit
- [ ] Multisig for admin functions
- [ ] Timelock for critical changes
- [ ] Emergency pause mechanism
- [ ] Monitoring and alerts configured
- [ ] Bug bounty program launched
