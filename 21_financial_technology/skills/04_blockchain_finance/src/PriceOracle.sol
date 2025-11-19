// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

contract PriceOracle {
    mapping(address => uint256) public prices;
    mapping(address => uint256) public lastUpdated;
    address public admin;

    event PriceUpdated(address indexed token, uint256 price);

    constructor() {
        admin = msg.sender;
    }

    function updatePrice(address token, uint256 price) external {
        require(msg.sender == admin, "Only admin");
        prices[token] = price;
        lastUpdated[token] = block.timestamp;
        emit PriceUpdated(token, price);
    }

    function getPrice(address token) external view returns (uint256) {
        require(block.timestamp - lastUpdated[token] < 1 hours, "Price stale");
        return prices[token];
    }
}
