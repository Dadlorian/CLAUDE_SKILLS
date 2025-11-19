// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title SimpleAMM - Constant Product Market Maker
 * @dev Implements x * y = k formula for decentralized trading
 */
contract SimpleAMM is ReentrancyGuard {
    IERC20 public tokenA;
    IERC20 public tokenB;

    uint256 public reserveA;
    uint256 public reserveB;
    
    uint256 public totalLPSupply;
    mapping(address => uint256) public lpBalance;

    uint256 constant SWAP_FEE = 30; // 0.3%
    uint256 constant FEE_DENOMINATOR = 10000;

    event Swap(address indexed user, uint256 amountIn, uint256 amountOut);
    event Liquidity(address indexed provider, uint256 amountA, uint256 amountB, uint256 lpTokens);

    constructor(IERC20 _tokenA, IERC20 _tokenB) {
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    /**
     * @dev Add liquidity to pool
     */
    function addLiquidity(uint256 amountA, uint256 amountB) external nonReentrant returns (uint256) {
        require(amountA > 0 && amountB > 0, "Invalid amounts");

        tokenA.transferFrom(msg.sender, address(this), amountA);
        tokenB.transferFrom(msg.sender, address(this), amountB);

        uint256 lpTokens;
        if (totalLPSupply == 0) {
            lpTokens = sqrt(amountA * amountB);
        } else {
            uint256 lpFromA = (amountA * totalLPSupply) / reserveA;
            uint256 lpFromB = (amountB * totalLPSupply) / reserveB;
            lpTokens = min(lpFromA, lpFromB);
        }

        require(lpTokens > 0, "Insufficient liquidity minted");

        reserveA += amountA;
        reserveB += amountB;
        totalLPSupply += lpTokens;
        lpBalance[msg.sender] += lpTokens;

        emit Liquidity(msg.sender, amountA, amountB, lpTokens);
        return lpTokens;
    }

    /**
     * @dev Remove liquidity from pool
     */
    function removeLiquidity(uint256 lpTokens) external nonReentrant returns (uint256, uint256) {
        require(lpBalance[msg.sender] >= lpTokens, "Insufficient LP tokens");

        uint256 amountA = (lpTokens * reserveA) / totalLPSupply;
        uint256 amountB = (lpTokens * reserveB) / totalLPSupply;

        lpBalance[msg.sender] -= lpTokens;
        totalLPSupply -= lpTokens;
        reserveA -= amountA;
        reserveB -= amountB;

        tokenA.transfer(msg.sender, amountA);
        tokenB.transfer(msg.sender, amountB);

        emit Liquidity(msg.sender, amountA, amountB, lpTokens);
        return (amountA, amountB);
    }

    /**
     * @dev Swap tokenA for tokenB
     */
    function swapAforB(uint256 amountA) external nonReentrant returns (uint256) {
        require(amountA > 0, "Invalid amount");

        tokenA.transferFrom(msg.sender, address(this), amountA);

        uint256 fee = (amountA * SWAP_FEE) / FEE_DENOMINATOR;
        uint256 amountAAfterFee = amountA - fee;

        uint256 amountB = (reserveB * amountAAfterFee) / (reserveA + amountAAfterFee);
        require(amountB > 0, "Insufficient output");

        reserveA += amountAAfterFee;
        reserveB -= amountB;

        tokenB.transfer(msg.sender, amountB);
        emit Swap(msg.sender, amountA, amountB);

        return amountB;
    }

    /**
     * @dev Swap tokenB for tokenA
     */
    function swapBforA(uint256 amountB) external nonReentrant returns (uint256) {
        require(amountB > 0, "Invalid amount");

        tokenB.transferFrom(msg.sender, address(this), amountB);

        uint256 fee = (amountB * SWAP_FEE) / FEE_DENOMINATOR;
        uint256 amountBAfterFee = amountB - fee;

        uint256 amountA = (reserveA * amountBAfterFee) / (reserveB + amountBAfterFee);
        require(amountA > 0, "Insufficient output");

        reserveB += amountBAfterFee;
        reserveA -= amountA;

        tokenA.transfer(msg.sender, amountA);
        emit Swap(msg.sender, amountB, amountA);

        return amountA;
    }

    /**
     * @dev Get output amount for input
     */
    function getAmountOut(uint256 amountIn, bool tokenAtoB) external view returns (uint256) {
        uint256 fee = (amountIn * SWAP_FEE) / FEE_DENOMINATOR;
        uint256 amountInAfterFee = amountIn - fee;

        if (tokenAtoB) {
            return (reserveB * amountInAfterFee) / (reserveA + amountInAfterFee);
        } else {
            return (reserveA * amountInAfterFee) / (reserveB + amountInAfterFee);
        }
    }

    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}
