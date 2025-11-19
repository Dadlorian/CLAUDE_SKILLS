// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Capped.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MyToken - Production-Ready ERC20 Token
 * @dev Implements standard ERC20 with burn, cap, and minting capabilities
 */
contract MyToken is ERC20, ERC20Burnable, ERC20Capped, Ownable {
    uint256 private constant INITIAL_SUPPLY = 1_000_000 * 10 ** 18;
    uint256 private constant MAX_SUPPLY = 10_000_000 * 10 ** 18;

    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);

    constructor() ERC20("My Token", "MTK") ERC20Capped(MAX_SUPPLY) {
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    /**
     * @dev Mint new tokens (only owner)
     * @param to Recipient address
     * @param amount Amount to mint
     */
    function mint(address to, uint256 amount) public onlyOwner {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Amount must be greater than 0");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @dev Burn tokens from caller's balance
     * @param amount Amount to burn
     */
    function burn(uint256 amount) public override(ERC20Burnable) {
        super.burn(amount);
        emit TokensBurned(msg.sender, amount);
    }

    /**
     * @dev Required override for ERC20 and ERC20Capped
     */
    function _mint(address to, uint256 amount)
        internal
        override(ERC20, ERC20Capped)
    {
        super._mint(to, amount);
    }

    /**
     * @dev Get total supply
     */
    function totalSupply() public view override returns (uint256) {
        return super.totalSupply();
    }

    /**
     * @dev Get token decimals
     */
    function decimals() public pure override returns (uint8) {
        return 18;
    }
}
