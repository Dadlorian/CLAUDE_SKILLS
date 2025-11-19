// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

/**
 * @title MultiSigWallet - Multi-signature wallet for secure fund management
 */
contract MultiSigWallet {
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public requiredConfirmations;

    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 confirmations;
    }

    Transaction[] public transactions;
    mapping(uint256 => mapping(address => bool)) public confirmations;

    event Deposit(address indexed sender, uint256 amount);
    event SubmitTransaction(uint256 indexed txIndex, address indexed owner, address indexed to, uint256 value);
    event ConfirmTransaction(uint256 indexed txIndex, address indexed owner);
    event ExecuteTransaction(uint256 indexed txIndex);

    constructor(address[] memory _owners, uint256 _requiredConfirmations) {
        require(_owners.length > 0, "Owners required");
        require(_requiredConfirmations > 0 && _requiredConfirmations <= _owners.length, "Invalid confirmations");

        for (uint256 i = 0; i < _owners.length; i++) {
            require(_owners[i] != address(0), "Invalid owner");
            require(!isOwner[_owners[i]], "Owner not unique");
            
            owners.push(_owners[i]);
            isOwner[_owners[i]] = true;
        }

        requiredConfirmations = _requiredConfirmations;
    }

    receive() external payable {
        emit Deposit(msg.sender, msg.value);
    }

    /**
     * @dev Submit transaction for confirmation
     */
    function submitTransaction(address _to, uint256 _value, bytes memory _data) public {
        require(isOwner[msg.sender], "Not owner");
        
        uint256 txIndex = transactions.length;
        transactions.push(Transaction({
            to: _to,
            value: _value,
            data: _data,
            executed: false,
            confirmations: 0
        }));

        emit SubmitTransaction(txIndex, msg.sender, _to, _value);
    }

    /**
     * @dev Confirm transaction
     */
    function confirmTransaction(uint256 _txIndex) public {
        require(isOwner[msg.sender], "Not owner");
        require(_txIndex < transactions.length, "Invalid transaction");
        require(!confirmations[_txIndex][msg.sender], "Already confirmed");

        confirmations[_txIndex][msg.sender] = true;
        transactions[_txIndex].confirmations += 1;

        emit ConfirmTransaction(_txIndex, msg.sender);
    }

    /**
     * @dev Execute transaction if confirmed by required signers
     */
    function executeTransaction(uint256 _txIndex) public {
        require(_txIndex < transactions.length, "Invalid transaction");
        
        Transaction storage transaction = transactions[_txIndex];
        require(transaction.confirmations >= requiredConfirmations, "Not enough confirmations");
        require(!transaction.executed, "Already executed");

        transaction.executed = true;

        (bool success, ) = transaction.to.call{value: transaction.value}(transaction.data);
        require(success, "Transaction failed");

        emit ExecuteTransaction(_txIndex);
    }

    /**
     * @dev Get transaction count
     */
    function getTransactionCount() public view returns (uint256) {
        return transactions.length;
    }

    /**
     * @dev Get wallet balance
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
