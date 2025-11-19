# Flash Loans Guide

## Flash Loan Basics

### Aave Flash Loan
```solidity
pragma solidity ^0.8.9;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IFlashLoanReceiver.sol";

contract FlashLoanExample is FlashLoanReceiverBase {
    IPool public immutable lendingPool;
    ISwapRouter public immutable uniswapRouter;

    constructor(address _lendingPool, address _uniswapRouter)
        FlashLoanReceiverBase(IPoolAddressesProvider(_lendingPool))
    {
        lendingPool = IPool(_lendingPool);
        uniswapRouter = ISwapRouter(_uniswapRouter);
    }

    function executeFlashLoan(
        address asset,
        uint256 amount
    ) external {
        address receiver = address(this);
        address[] memory assets = new address[](1);
        assets[0] = asset;

        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amount;

        uint256[] memory modes = new uint256[](1);
        modes[0] = 0; // No debt, repay

        lendingPool.flashLoan(
            receiver,
            assets,
            amounts,
            modes,
            address(this),
            "",
            0
        );
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bytes32) {
        // 1. Execute arbitrage or other operation
        uint256 amountOwed = amount + premium;

        // 2. Use borrowed funds
        // Example: Arbitrage between DEXes

        // 3. Approve repayment
        IERC20(asset).approve(address(lendingPool), amountOwed);

        return keccak256("ERC3156FlashBorrower.onFlashLoan");
    }
}
```

## Arbitrage with Flash Loans

### Token Arbitrage Pattern
```solidity
contract FlashLoanArbitrage is IFlashLoanReceiver {
    address public constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    function executeFlashLoanAndArbitrage(uint256 usdcAmount) external {
        // Borrow USDC
        bytes memory data = abi.encode(usdcAmount);

        lendingPool.flashLoan(
            address(this),
            USDC,
            usdcAmount,
            data
        );
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata data
    ) external override returns (bytes32) {
        // 1. Buy ETH on Uniswap V2
        uint256 wethAmount = buyOnUniswapV2(USDC, WETH, amount);

        // 2. Sell ETH on Uniswap V3 for profit
        uint256 usdcReceived = sellOnUniswapV3(WETH, USDC, wethAmount);

        // 3. Repay flash loan
        uint256 amountOwed = amount + premium;
        IERC20(USDC).approve(address(lendingPool), amountOwed);

        // 4. Keep profit
        uint256 profit = usdcReceived - amountOwed;
        IERC20(USDC).transfer(msg.sender, profit);

        return keccak256("ERC3156FlashBorrower.onFlashLoan");
    }

    function buyOnUniswapV2(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256) {
        // Swap logic
    }

    function sellOnUniswapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256) {
        // Swap logic
    }
}
```

## Liquidation with Flash Loans

### Liquidation Execution
```solidity
contract FlashLoanLiquidation is IFlashLoanReceiver {
    ILendingPool public lendingPool;
    IUniswapRouter public router;

    function liquidateWithFlashLoan(
        address borrowerAddress,
        uint256 borrowAmount
    ) external {
        lendingPool.flashLoan(
            address(this),
            stablecoin,
            borrowAmount,
            abi.encode(borrowerAddress)
        );
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata data
    ) external override returns (bytes32) {
        address borrower = abi.decode(data, (address));

        // 1. Execute liquidation
        lendingPool.liquidationCall(
            collateralAsset,
            asset,
            borrower,
            amount,
            false
        );

        // 2. Swap seized collateral for stablecoin
        uint256 collateralReceived = IERC20(collateralAsset).balanceOf(address(this));
        uint256 stablecoinReceived = swapCollateralToStablecoin(
            collateralAsset,
            asset,
            collateralReceived
        );

        // 3. Repay flash loan
        uint256 amountOwed = amount + premium;
        require(stablecoinReceived >= amountOwed, "Not enough to repay");

        IERC20(asset).approve(address(lendingPool), amountOwed);

        // 4. Keep profit
        uint256 profit = stablecoinReceived - amountOwed;
        IERC20(asset).transfer(msg.sender, profit);

        return keccak256("ERC3156FlashBorrower.onFlashLoan");
    }
}
```

## Risks and Security

### Flash Loan Attack Vectors
```
1. Oracle Manipulation: Use borrowed tokens to crash price
2. Complex Interactions: Unexpected contract behavior
3. Reentrancy: During flash loan operations
4. Insufficient Checks: Forgetting to repay
```

### Security Measures
```solidity
// Use ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SafeFlashLoan is ReentrancyGuard {
    function executeOperation(...) external nonReentrant {
        // Protected from reentrancy
    }
}

// Verify oracle prices
function getPrice(address token) internal view returns (uint256) {
    // Use TWAP (time-weighted average price)
    // Avoid spot price manipulation
}

// Check repayment before completion
require(
    IERC20(asset).balanceOf(address(this)) >= amountOwed,
    "Insufficient balance"
);
```

## Testing Flash Loans

```javascript
describe("Flash Loan Arbitrage", function() {
  it("Should execute arbitrage and profit", async function() {
    const borrowAmount = ethers.parseEther("1000");

    const tx = await flashLoan.executeFlashLoanAndArbitrage(borrowAmount);
    await tx.wait();

    // Verify profit was transferred
    const balance = await usdc.balanceOf(owner.address);
    expect(balance).to.be.gt(ethers.parseEther("100")); // Profit threshold
  });

  it("Should revert if repayment insufficient", async function() {
    // Test scenarios where trade fails
    // Verify transaction reverts properly
  });
});
```

---

**Key Takeaways**:
- Flash loans enable 0-collateral borrows
- Must repay within same transaction
- No real way to default (tx reverts)
- Use for arbitrage, liquidation, refinancing
- Be aware of oracle and reentrancy risks
