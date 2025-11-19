# AMM Implementation Guide

## Basic AMM Contract

### Constant Product Formula
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SimpleAMM {
    IERC20 public tokenA;
    IERC20 public tokenB;

    uint256 public reserveA;
    uint256 public reserveB;

    uint256 public totalLPSupply;
    mapping(address => uint256) public lpBalance;

    event Swap(address indexed swapper, uint256 amountIn, uint256 amountOut);
    event Deposit(address indexed provider, uint256 amountA, uint256 amountB, uint256 lpTokens);
    event Withdraw(address indexed provider, uint256 amountA, uint256 amountB, uint256 lpTokens);

    constructor(IERC20 _tokenA, IERC20 _tokenB) {
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    // Add liquidity
    function addLiquidity(uint256 amountA, uint256 amountB) public returns (uint256) {
        require(amountA > 0 && amountB > 0, "Invalid amounts");

        // Transfer tokens from user
        tokenA.transferFrom(msg.sender, address(this), amountA);
        tokenB.transferFrom(msg.sender, address(this), amountB);

        uint256 lpTokens;
        if (totalLPSupply == 0) {
            // First LP: Create initial share
            lpTokens = sqrt(amountA * amountB);
        } else {
            // Subsequent LPs: Proportional share
            uint256 lpFromA = (amountA * totalLPSupply) / reserveA;
            uint256 lpFromB = (amountB * totalLPSupply) / reserveB;
            lpTokens = min(lpFromA, lpFromB);
        }

        require(lpTokens > 0, "Insufficient liquidity minted");

        // Update reserves and LP balance
        reserveA += amountA;
        reserveB += amountB;
        totalLPSupply += lpTokens;
        lpBalance[msg.sender] += lpTokens;

        emit Deposit(msg.sender, amountA, amountB, lpTokens);
        return lpTokens;
    }

    // Remove liquidity
    function removeLiquidity(uint256 lpTokens) public returns (uint256, uint256) {
        require(lpBalance[msg.sender] >= lpTokens, "Insufficient LP tokens");

        // Calculate amounts
        uint256 amountA = (lpTokens * reserveA) / totalLPSupply;
        uint256 amountB = (lpTokens * reserveB) / totalLPSupply;

        // Update state
        lpBalance[msg.sender] -= lpTokens;
        totalLPSupply -= lpTokens;
        reserveA -= amountA;
        reserveB -= amountB;

        // Transfer tokens
        tokenA.transfer(msg.sender, amountA);
        tokenB.transfer(msg.sender, amountB);

        emit Withdraw(msg.sender, amountA, amountB, lpTokens);
        return (amountA, amountB);
    }

    // Swap token A for token B
    function swapAforB(uint256 amountA) public returns (uint256) {
        require(amountA > 0, "Invalid amount");

        // Transfer input tokens
        tokenA.transferFrom(msg.sender, address(this), amountA);

        // Calculate output: (x + dx) * (y - dy) = x * y
        // (reserveA + amountA) * (reserveB - amountOut) = reserveA * reserveB
        // amountOut = reserveB - (reserveA * reserveB) / (reserveA + amountA)

        uint256 numerator = reserveB * amountA;
        uint256 denominator = reserveA + amountA;
        uint256 amountOut = reserveB - (reserveA * reserveB) / denominator;

        require(amountOut > 0, "Insufficient liquidity");

        // Update reserves
        reserveA += amountA;
        reserveB -= amountOut;

        // Transfer output
        tokenB.transfer(msg.sender, amountOut);

        emit Swap(msg.sender, amountA, amountOut);
        return amountOut;
    }

    // Swap token B for token A
    function swapBforA(uint256 amountB) public returns (uint256) {
        require(amountB > 0, "Invalid amount");

        tokenB.transferFrom(msg.sender, address(this), amountB);

        uint256 amountOut = reserveA - (reserveA * reserveB) / (reserveB + amountB);

        require(amountOut > 0, "Insufficient liquidity");

        reserveB += amountB;
        reserveA -= amountOut;

        tokenA.transfer(msg.sender, amountOut);

        emit Swap(msg.sender, amountB, amountOut);
        return amountOut;
    }

    // Get amount out for given input
    function getAmountOut(uint256 amountIn, bool tokenAforB) public view returns (uint256) {
        if (tokenAforB) {
            return reserveB - (reserveA * reserveB) / (reserveA + amountIn);
        } else {
            return reserveA - (reserveA * reserveB) / (reserveB + amountIn);
        }
    }

    // Helper functions
    function sqrt(uint256 x) private pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    function min(uint256 a, uint256 b) private pure returns (uint256) {
        return a < b ? a : b;
    }
}
```

## Testing the AMM

```javascript
describe("SimpleAMM", function () {
  let amm, tokenA, tokenB, owner, user1;

  beforeEach(async function () {
    [owner, user1] = await ethers.getSigners();

    // Deploy tokens
    const Token = await ethers.getContractFactory("ERC20Mock");
    tokenA = await Token.deploy("Token A", "TKA");
    tokenB = await Token.deploy("Token B", "TKB");

    // Deploy AMM
    const AMM = await ethers.getContractFactory("SimpleAMM");
    amm = await AMM.deploy(tokenA.address, tokenB.address);

    // Mint tokens
    await tokenA.mint(owner.address, ethers.parseEther("1000"));
    await tokenB.mint(owner.address, ethers.parseEther("1000"));

    // Approve AMM
    await tokenA.approve(amm.address, ethers.MaxUint256);
    await tokenB.approve(amm.address, ethers.MaxUint256);
  });

  it("Should add liquidity", async function () {
    const amountA = ethers.parseEther("10");
    const amountB = ethers.parseEther("10");

    const tx = await amm.addLiquidity(amountA, amountB);
    await tx.wait();

    const reserve0 = await amm.reserveA();
    const reserve1 = await amm.reserveB();

    expect(reserve0).to.equal(amountA);
    expect(reserve1).to.equal(amountB);
  });

  it("Should execute swap", async function () {
    await amm.addLiquidity(
      ethers.parseEther("100"),
      ethers.parseEther("100")
    );

    const swapAmount = ethers.parseEther("10");
    const amountOut = await amm.getAmountOut(swapAmount, true);

    const tx = await amm.swapAforB(swapAmount);
    await tx.wait();

    expect(amountOut).to.be.gt(0);
  });

  it("Should calculate price correctly", async function () {
    await amm.addLiquidity(
      ethers.parseEther("100"),
      ethers.parseEther("200")
    );

    // Price should be 200/100 = 2
    const amountOut = await amm.getAmountOut(ethers.parseEther("1"), true);
    expect(amountOut).to.be.closeTo(ethers.parseEther("1.98"), ethers.parseEther("0.01"));
  });
});
```

## Optimization Strategies

### Flash Swaps
```solidity
interface IFlashSwapCallback {
    function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) external;
}

contract FlashSwapArbotrage is IFlashSwapCallback {
    function executeArbitrage(address tokenA, address tokenB, uint256 amount) external {
        // Call pair.swap() with custom callback
        // callback will execute arbitrage logic
    }

    function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) external {
        // Execute arbitrage
        // Repay flash loan + fee
    }
}
```

### Gas Optimization
```solidity
// Store reserves in single slot
contract GasOptimizedAMM {
    struct Reserves {
        uint112 reserveA;
        uint112 reserveB;
        uint32 blockTimestamp;
    }

    Reserves private reserves;

    function getReserves() public view returns (uint112, uint112, uint32) {
        return (reserves.reserveA, reserves.reserveB, reserves.blockTimestamp);
    }
}
```

## Deployment and Integration

```bash
# Compile and deploy
npx hardhat compile
npx hardhat run scripts/deploy-amm.js --network localhost

# Verify on block explorer
npx hardhat verify --network sepolia <AMM_ADDRESS> <TOKEN_A> <TOKEN_B>

# Test on testnet
npx hardhat test --network sepolia
```

---

**Key Takeaways**:
- x*y=k formula ensures price discovery
- LP fees incentivize liquidity provision
- Slippage increases with trade size
- Concentrated liquidity improves capital efficiency
- Testing is critical for financial contracts
