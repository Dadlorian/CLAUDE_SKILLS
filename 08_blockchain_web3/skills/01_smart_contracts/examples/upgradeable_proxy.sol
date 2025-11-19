// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title TransparentUpgradeableProxy
 * @dev Production-ready upgradeable proxy implementation
 * Implements EIP-1967 transparent proxy pattern
 */
contract TransparentUpgradeableProxy {
    // Storage slot for implementation address
    // keccak256("eip1967.proxy.implementation") - 1
    bytes32 private constant IMPLEMENTATION_SLOT =
        0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    // Storage slot for admin address
    // keccak256("eip1967.proxy.admin") - 1
    bytes32 private constant ADMIN_SLOT =
        0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103;

    event Upgraded(address indexed implementation);
    event AdminChanged(address previousAdmin, address newAdmin);

    /**
     * @dev Constructor sets initial implementation and admin
     */
    constructor(address _implementation, address _admin) {
        _setImplementation(_implementation);
        _setAdmin(_admin);
    }

    /**
     * @dev Modifier to check if caller is admin
     */
    modifier ifAdmin() {
        if (msg.sender == _getAdmin()) {
            _;
        } else {
            _fallback();
        }
    }

    /**
     * @dev Fallback function delegates calls to implementation
     */
    fallback() external payable {
        _fallback();
    }

    /**
     * @dev Receive function to accept ETH
     */
    receive() external payable {
        _fallback();
    }

    /**
     * @dev Upgrade to new implementation
     * @param newImplementation Address of new implementation
     */
    function upgradeTo(address newImplementation) external ifAdmin {
        _upgradeTo(newImplementation);
    }

    /**
     * @dev Upgrade and call new implementation
     * @param newImplementation Address of new implementation
     * @param data Calldata to execute on new implementation
     */
    function upgradeToAndCall(address newImplementation, bytes calldata data)
        external
        payable
        ifAdmin
    {
        _upgradeTo(newImplementation);
        (bool success, ) = newImplementation.delegatecall(data);
        require(success, "Upgrade call failed");
    }

    /**
     * @dev Change admin address
     * @param newAdmin Address of new admin
     */
    function changeAdmin(address newAdmin) external ifAdmin {
        require(newAdmin != address(0), "Invalid admin address");
        emit AdminChanged(_getAdmin(), newAdmin);
        _setAdmin(newAdmin);
    }

    /**
     * @dev Get current admin
     */
    function admin() external ifAdmin returns (address) {
        return _getAdmin();
    }

    /**
     * @dev Get current implementation
     */
    function implementation() external ifAdmin returns (address) {
        return _getImplementation();
    }

    /**
     * @dev Internal function to delegate calls
     */
    function _fallback() internal {
        _delegate(_getImplementation());
    }

    /**
     * @dev Delegate call to implementation
     */
    function _delegate(address impl) internal {
        assembly {
            // Copy msg.data
            calldatacopy(0, 0, calldatasize())

            // Delegate call to implementation
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)

            // Copy return data
            returndatacopy(0, 0, returndatasize())

            switch result
            case 0 {
                revert(0, returndatasize())
            }
            default {
                return(0, returndatasize())
            }
        }
    }

    /**
     * @dev Upgrade to new implementation
     */
    function _upgradeTo(address newImplementation) internal {
        require(
            newImplementation != address(0) &&
            _isContract(newImplementation),
            "Invalid implementation"
        );
        _setImplementation(newImplementation);
        emit Upgraded(newImplementation);
    }

    /**
     * @dev Get implementation address from storage
     */
    function _getImplementation() internal view returns (address impl) {
        bytes32 slot = IMPLEMENTATION_SLOT;
        assembly {
            impl := sload(slot)
        }
    }

    /**
     * @dev Set implementation address in storage
     */
    function _setImplementation(address newImplementation) internal {
        bytes32 slot = IMPLEMENTATION_SLOT;
        assembly {
            sstore(slot, newImplementation)
        }
    }

    /**
     * @dev Get admin address from storage
     */
    function _getAdmin() internal view returns (address adm) {
        bytes32 slot = ADMIN_SLOT;
        assembly {
            adm := sload(slot)
        }
    }

    /**
     * @dev Set admin address in storage
     */
    function _setAdmin(address newAdmin) internal {
        bytes32 slot = ADMIN_SLOT;
        assembly {
            sstore(slot, newAdmin)
        }
    }

    /**
     * @dev Check if address is a contract
     */
    function _isContract(address account) internal view returns (bool) {
        uint256 size;
        assembly {
            size := extcodesize(account)
        }
        return size > 0;
    }
}

/**
 * @title ProxyAdmin
 * @dev Admin contract for managing proxy upgrades
 */
contract ProxyAdmin {
    address public owner;

    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @dev Transfer ownership
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    /**
     * @dev Get implementation of proxy
     */
    function getProxyImplementation(TransparentUpgradeableProxy proxy)
        external
        view
        returns (address)
    {
        (bool success, bytes memory returndata) = address(proxy).staticcall(
            abi.encodeWithSignature("implementation()")
        );
        require(success, "Call failed");
        return abi.decode(returndata, (address));
    }

    /**
     * @dev Get admin of proxy
     */
    function getProxyAdmin(TransparentUpgradeableProxy proxy)
        external
        view
        returns (address)
    {
        (bool success, bytes memory returndata) = address(proxy).staticcall(
            abi.encodeWithSignature("admin()")
        );
        require(success, "Call failed");
        return abi.decode(returndata, (address));
    }

    /**
     * @dev Upgrade proxy to new implementation
     */
    function upgrade(
        TransparentUpgradeableProxy proxy,
        address implementation
    ) external onlyOwner {
        proxy.upgradeTo(implementation);
    }

    /**
     * @dev Upgrade and call
     */
    function upgradeAndCall(
        TransparentUpgradeableProxy proxy,
        address implementation,
        bytes memory data
    ) external payable onlyOwner {
        proxy.upgradeToAndCall{value: msg.value}(implementation, data);
    }
}
