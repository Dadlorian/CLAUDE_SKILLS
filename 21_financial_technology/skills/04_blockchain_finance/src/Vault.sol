// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title Vault - Yield-bearing vault (ERC4626)
 */
contract Vault is ERC20 {
    IERC20 public asset;
    uint256 public totalAssets;

    constructor(IERC20 _asset) ERC20("Vault Token", "vToken") {
        asset = _asset;
    }

    function deposit(uint256 assets, address receiver) public returns (uint256 shares) {
        if (totalAssets == 0) {
            shares = assets;
        } else {
            shares = (assets * totalSupply()) / totalAssets;
        }
        
        asset.transferFrom(msg.sender, address(this), assets);
        totalAssets += assets;
        _mint(receiver, shares);
    }

    function withdraw(uint256 assets, address receiver, address owner) public returns (uint256 shares) {
        shares = (assets * totalSupply()) / totalAssets;
        
        _burn(owner, shares);
        totalAssets -= assets;
        asset.transfer(receiver, assets);
    }

    function convertToAssets(uint256 shares) public view returns (uint256) {
        if (totalSupply() == 0) return shares;
        return (shares * totalAssets) / totalSupply();
    }

    function convertToShares(uint256 assets) public view returns (uint256) {
        if (totalAssets == 0) return assets;
        return (assets * totalSupply()) / totalAssets;
    }
}
