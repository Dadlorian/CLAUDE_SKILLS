# Contract Upgradeability Patterns

## 1. Transparent Proxy Pattern

```solidity
contract TransparentProxy {
    address public implementation;
    address public admin;

    fallback() external payable {
        if (msg.sender == admin) {
            // Admin calls go to proxy
        } else {
            // User calls delegated to implementation
            (bool success, ) = implementation.delegatecall(msg.data);
            require(success);
        }
    }
}
```

**Pros**: Clear admin/user separation
**Cons**: Higher gas for admin

## 2. UUPS (Universal Upgradeable Proxy Standard)

```solidity
contract UUPSProxy {
    address public implementation;

    fallback() external payable {
        (bool success, ) = implementation.delegatecall(msg.data);
        require(success);
    }
}

contract Implementation {
    address public implementation; // Matches proxy storage

    function upgradeTo(address newImpl) public onlyOwner {
        implementation = newImpl;
    }
}
```

**Pros**: Lower gas costs
**Cons**: Upgrade logic in implementation (risky if buggy)

## 3. Diamond Pattern (EIP-2535)

```solidity
contract Diamond {
    mapping(bytes4 => address) public facets;

    fallback() external payable {
        address facet = facets[msg.sig];
        require(facet != address(0));
        (bool success, ) = facet.delegatecall(msg.data);
        require(success);
    }
}
```

**Pros**: Unlimited size, modular upgrades
**Cons**: Complex, higher gas

## Storage Gaps

```solidity
contract UpgradeableV1 {
    uint256 public value1;
    uint256[49] private __gap; // Reserve 49 slots
}

contract UpgradeableV2 is UpgradeableV1 {
    uint256 public value2; // Uses first gap slot
    // __gap now 48 slots
}
```
