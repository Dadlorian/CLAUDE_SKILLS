// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract LiquidityPool is ERC20 {
    IERC20 public token0;
    IERC20 public token1;

    uint256 public reserve0;
    uint256 public reserve1;

    constructor(IERC20 _token0, IERC20 _token1) ERC20("LP Token", "LP") {
        token0 = _token0;
        token1 = _token1;
    }

    function addLiquidity(uint256 amount0, uint256 amount1) external {
        token0.transferFrom(msg.sender, address(this), amount0);
        token1.transferFrom(msg.sender, address(this), amount1);

        reserve0 += amount0;
        reserve1 += amount1;

        uint256 lpTokens = (amount0 + amount1) / 2;
        _mint(msg.sender, lpTokens);
    }

    function removeLiquidity(uint256 lpTokens) external {
        uint256 amount0 = (lpTokens * reserve0) / totalSupply();
        uint256 amount1 = (lpTokens * reserve1) / totalSupply();

        _burn(msg.sender, lpTokens);
        reserve0 -= amount0;
        reserve1 -= amount1;

        token0.transfer(msg.sender, amount0);
        token1.transfer(msg.sender, amount1);
    }
}
