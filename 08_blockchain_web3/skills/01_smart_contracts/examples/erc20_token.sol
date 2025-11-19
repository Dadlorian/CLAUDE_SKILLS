// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/**
 * @title AdvancedERC20Token
 * @dev Production-ready ERC20 token with advanced features:
 * - Role-based access control
 * - Pausable transfers
 * - Burnable tokens
 * - EIP-2612 Permit (gasless approvals)
 * - Max supply cap
 * - Initial supply distribution
 */
contract AdvancedERC20Token is
    ERC20,
    ERC20Burnable,
    ERC20Pausable,
    AccessControl,
    ERC20Permit
{
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    uint256 public immutable MAX_SUPPLY;

    event TokensMinted(address indexed to, uint256 amount);
    event MaxSupplyReached();

    /**
     * @dev Constructor initializes the token with name, symbol, and max supply
     * @param name Token name
     * @param symbol Token symbol
     * @param maxSupply Maximum token supply
     * @param initialSupply Initial supply to mint to deployer
     */
    constructor(
        string memory name,
        string memory symbol,
        uint256 maxSupply,
        uint256 initialSupply
    ) ERC20(name, symbol) ERC20Permit(name) {
        require(maxSupply > 0, "Max supply must be greater than 0");
        require(initialSupply <= maxSupply, "Initial supply exceeds max supply");

        MAX_SUPPLY = maxSupply;

        // Grant roles to deployer
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);

        // Mint initial supply
        if (initialSupply > 0) {
            _mint(msg.sender, initialSupply);
        }
    }

    /**
     * @dev Pauses all token transfers
     * Can only be called by accounts with PAUSER_ROLE
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @dev Unpauses all token transfers
     * Can only be called by accounts with PAUSER_ROLE
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Mints new tokens up to MAX_SUPPLY
     * Can only be called by accounts with MINTER_ROLE
     * @param to Address to receive minted tokens
     * @param amount Amount of tokens to mint
     */
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        require(to != address(0), "Cannot mint to zero address");
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");

        _mint(to, amount);
        emit TokensMinted(to, amount);

        if (totalSupply() == MAX_SUPPLY) {
            emit MaxSupplyReached();
        }
    }

    /**
     * @dev Batch transfer to multiple addresses
     * @param recipients Array of recipient addresses
     * @param amounts Array of amounts to transfer
     */
    function batchTransfer(
        address[] calldata recipients,
        uint256[] calldata amounts
    ) external returns (bool) {
        require(recipients.length == amounts.length, "Arrays length mismatch");
        require(recipients.length <= 200, "Too many recipients");

        uint256 totalAmount;
        for (uint256 i = 0; i < recipients.length; ) {
            totalAmount += amounts[i];
            unchecked { ++i; }
        }

        require(balanceOf(msg.sender) >= totalAmount, "Insufficient balance");

        for (uint256 i = 0; i < recipients.length; ) {
            _transfer(msg.sender, recipients[i], amounts[i]);
            unchecked { ++i; }
        }

        return true;
    }

    /**
     * @dev Required override for ERC20Pausable
     */
    function _update(
        address from,
        address to,
        uint256 value
    ) internal override(ERC20, ERC20Pausable) {
        super._update(from, to, value);
    }

    /**
     * @dev Returns the number of decimals used by the token
     */
    function decimals() public pure override returns (uint8) {
        return 18;
    }

    /**
     * @dev Check remaining mintable supply
     */
    function remainingSupply() external view returns (uint256) {
        return MAX_SUPPLY - totalSupply();
    }
}
