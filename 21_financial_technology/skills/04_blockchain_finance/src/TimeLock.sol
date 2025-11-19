// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

contract TimeLock {
    mapping(bytes32 => uint256) public queuedTransactions;
    uint256 public constant DELAY = 2 days;

    event TransactionQueued(bytes32 txHash);
    event TransactionExecuted(bytes32 txHash);

    function queueTransaction(address target, uint256 value, bytes memory data) external returns (bytes32) {
        bytes32 txHash = keccak256(abi.encode(target, value, data));
        queuedTransactions[txHash] = block.timestamp + DELAY;
        emit TransactionQueued(txHash);
        return txHash;
    }

    function executeTransaction(address target, uint256 value, bytes memory data) external payable {
        bytes32 txHash = keccak256(abi.encode(target, value, data));
        require(queuedTransactions[txHash] != 0, "Not queued");
        require(block.timestamp >= queuedTransactions[txHash], "Delay not met");

        (bool success, ) = target.call{value: value}(data);
        require(success, "Execution failed");

        emit TransactionExecuted(txHash);
    }
}
