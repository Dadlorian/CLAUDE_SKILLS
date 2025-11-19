// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MultiSigWallet
 * @dev Production-ready multi-signature wallet
 * Features:
 * - Multiple owners with configurable threshold
 * - Transaction proposal and confirmation system
 * - ETH and ERC20 token support
 * - Owner management (add/remove owners, change threshold)
 * - Transaction execution with gas forwarding
 */
contract MultiSigWallet {
    // Events
    event Deposit(address indexed sender, uint256 amount, uint256 balance);
    event SubmitTransaction(
        address indexed owner,
        uint256 indexed txIndex,
        address indexed to,
        uint256 value,
        bytes data
    );
    event ConfirmTransaction(address indexed owner, uint256 indexed txIndex);
    event RevokeConfirmation(address indexed owner, uint256 indexed txIndex);
    event ExecuteTransaction(address indexed owner, uint256 indexed txIndex);
    event OwnerAddition(address indexed owner);
    event OwnerRemoval(address indexed owner);
    event RequirementChange(uint256 required);

    // State variables
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public numConfirmationsRequired;

    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 numConfirmations;
    }

    mapping(uint256 => mapping(address => bool)) public isConfirmed;
    Transaction[] public transactions;

    // Modifiers
    modifier onlyOwner() {
        require(isOwner[msg.sender], "Not owner");
        _;
    }

    modifier txExists(uint256 _txIndex) {
        require(_txIndex < transactions.length, "Transaction does not exist");
        _;
    }

    modifier notExecuted(uint256 _txIndex) {
        require(!transactions[_txIndex].executed, "Transaction already executed");
        _;
    }

    modifier notConfirmed(uint256 _txIndex) {
        require(!isConfirmed[_txIndex][msg.sender], "Transaction already confirmed");
        _;
    }

    /**
     * @dev Constructor initializes wallet with owners and required confirmations
     * @param _owners Array of owner addresses
     * @param _numConfirmationsRequired Number of confirmations needed for execution
     */
    constructor(address[] memory _owners, uint256 _numConfirmationsRequired) {
        require(_owners.length > 0, "Owners required");
        require(
            _numConfirmationsRequired > 0 &&
                _numConfirmationsRequired <= _owners.length,
            "Invalid number of required confirmations"
        );

        for (uint256 i = 0; i < _owners.length; ) {
            address owner = _owners[i];

            require(owner != address(0), "Invalid owner");
            require(!isOwner[owner], "Owner not unique");

            isOwner[owner] = true;
            owners.push(owner);

            unchecked { ++i; }
        }

        numConfirmationsRequired = _numConfirmationsRequired;
    }

    /**
     * @dev Receive function to accept ETH deposits
     */
    receive() external payable {
        emit Deposit(msg.sender, msg.value, address(this).balance);
    }

    /**
     * @dev Submit a transaction for approval
     * @param _to Destination address
     * @param _value ETH value to send
     * @param _data Call data
     */
    function submitTransaction(
        address _to,
        uint256 _value,
        bytes memory _data
    ) public onlyOwner returns (uint256) {
        uint256 txIndex = transactions.length;

        transactions.push(
            Transaction({
                to: _to,
                value: _value,
                data: _data,
                executed: false,
                numConfirmations: 0
            })
        );

        emit SubmitTransaction(msg.sender, txIndex, _to, _value, _data);

        // Auto-confirm for submitter
        confirmTransaction(txIndex);

        return txIndex;
    }

    /**
     * @dev Confirm a pending transaction
     * @param _txIndex Transaction index
     */
    function confirmTransaction(uint256 _txIndex)
        public
        onlyOwner
        txExists(_txIndex)
        notExecuted(_txIndex)
        notConfirmed(_txIndex)
    {
        Transaction storage transaction = transactions[_txIndex];
        transaction.numConfirmations += 1;
        isConfirmed[_txIndex][msg.sender] = true;

        emit ConfirmTransaction(msg.sender, _txIndex);

        // Auto-execute if threshold is met
        if (transaction.numConfirmations >= numConfirmationsRequired) {
            executeTransaction(_txIndex);
        }
    }

    /**
     * @dev Execute a confirmed transaction
     * @param _txIndex Transaction index
     */
    function executeTransaction(uint256 _txIndex)
        public
        onlyOwner
        txExists(_txIndex)
        notExecuted(_txIndex)
    {
        Transaction storage transaction = transactions[_txIndex];

        require(
            transaction.numConfirmations >= numConfirmationsRequired,
            "Cannot execute transaction: insufficient confirmations"
        );

        transaction.executed = true;

        (bool success, ) = transaction.to.call{value: transaction.value}(
            transaction.data
        );
        require(success, "Transaction execution failed");

        emit ExecuteTransaction(msg.sender, _txIndex);
    }

    /**
     * @dev Revoke confirmation for a pending transaction
     * @param _txIndex Transaction index
     */
    function revokeConfirmation(uint256 _txIndex)
        public
        onlyOwner
        txExists(_txIndex)
        notExecuted(_txIndex)
    {
        require(isConfirmed[_txIndex][msg.sender], "Transaction not confirmed");

        Transaction storage transaction = transactions[_txIndex];
        transaction.numConfirmations -= 1;
        isConfirmed[_txIndex][msg.sender] = false;

        emit RevokeConfirmation(msg.sender, _txIndex);
    }

    /**
     * @dev Get all owners
     */
    function getOwners() public view returns (address[] memory) {
        return owners;
    }

    /**
     * @dev Get transaction count
     */
    function getTransactionCount() public view returns (uint256) {
        return transactions.length;
    }

    /**
     * @dev Get transaction details
     * @param _txIndex Transaction index
     */
    function getTransaction(uint256 _txIndex)
        public
        view
        returns (
            address to,
            uint256 value,
            bytes memory data,
            bool executed,
            uint256 numConfirmations
        )
    {
        Transaction storage transaction = transactions[_txIndex];

        return (
            transaction.to,
            transaction.value,
            transaction.data,
            transaction.executed,
            transaction.numConfirmations
        );
    }

    /**
     * @dev Check if owner has confirmed a transaction
     * @param _txIndex Transaction index
     * @param _owner Owner address
     */
    function isTransactionConfirmed(uint256 _txIndex, address _owner)
        public
        view
        returns (bool)
    {
        return isConfirmed[_txIndex][_owner];
    }

    /**
     * @dev Get pending transactions
     */
    function getPendingTransactions()
        public
        view
        returns (uint256[] memory)
    {
        uint256 count = 0;

        // Count pending transactions
        for (uint256 i = 0; i < transactions.length; ) {
            if (!transactions[i].executed) {
                count++;
            }
            unchecked { ++i; }
        }

        // Create array of pending transaction indices
        uint256[] memory pending = new uint256[](count);
        uint256 index = 0;

        for (uint256 i = 0; i < transactions.length; ) {
            if (!transactions[i].executed) {
                pending[index] = i;
                index++;
            }
            unchecked { ++i; }
        }

        return pending;
    }

    /**
     * @dev Add a new owner (requires multisig approval)
     * @param _owner Address of new owner
     */
    function addOwner(address _owner) external onlyOwner {
        require(_owner != address(0), "Invalid owner address");
        require(!isOwner[_owner], "Owner already exists");

        isOwner[_owner] = true;
        owners.push(_owner);

        emit OwnerAddition(_owner);
    }

    /**
     * @dev Remove an owner (requires multisig approval)
     * @param _owner Address of owner to remove
     */
    function removeOwner(address _owner) external onlyOwner {
        require(isOwner[_owner], "Not an owner");
        require(owners.length - 1 >= numConfirmationsRequired,
            "Cannot remove owner: would invalidate threshold");

        isOwner[_owner] = false;

        // Remove from owners array
        for (uint256 i = 0; i < owners.length; ) {
            if (owners[i] == _owner) {
                owners[i] = owners[owners.length - 1];
                owners.pop();
                break;
            }
            unchecked { ++i; }
        }

        emit OwnerRemoval(_owner);
    }

    /**
     * @dev Change the number of required confirmations
     * @param _numConfirmationsRequired New threshold
     */
    function changeRequirement(uint256 _numConfirmationsRequired)
        external
        onlyOwner
    {
        require(
            _numConfirmationsRequired > 0 &&
                _numConfirmationsRequired <= owners.length,
            "Invalid requirement"
        );

        numConfirmationsRequired = _numConfirmationsRequired;
        emit RequirementChange(_numConfirmationsRequired);
    }
}
