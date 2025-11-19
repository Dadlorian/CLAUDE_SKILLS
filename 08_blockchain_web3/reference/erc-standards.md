# Smart Contract Standards (ERCs)

## Token Standards

### ERC-20 (Fungible Tokens)
**Use**: Standard tokens (USDC, LINK, UNI)

```solidity
interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}
```

### ERC-721 (NFTs)
**Use**: Unique tokens (CryptoPunks, BAYC)

```solidity
interface IERC721 {
    function balanceOf(address owner) external view returns (uint256);
    function ownerOf(uint256 tokenId) external view returns (address);
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function transferFrom(address from, address to, uint256 tokenId) external;
    function approve(address to, uint256 tokenId) external;
    function setApprovalForAll(address operator, bool approved) external;
    function getApproved(uint256 tokenId) external view returns (address);
    function isApprovedForAll(address owner, address operator) external view returns (bool);
}
```

### ERC-1155 (Multi-Token)
**Use**: Gaming assets, semi-fungibles

```solidity
interface IERC1155 {
    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata data) external;
    function safeBatchTransferFrom(address from, address to, uint256[] calldata ids, uint256[] calldata amounts, bytes calldata data) external;
    function balanceOf(address account, uint256 id) external view returns (uint256);
    function balanceOfBatch(address[] calldata accounts, uint256[] calldata ids) external view returns (uint256[] memory);
    function setApprovalForAll(address operator, bool approved) external;
    function isApprovedForAll(address account, address operator) external view returns (bool);
}
```

## Advanced Token Standards

### ERC-2612 (Permit - Gasless Approvals)
```solidity
function permit(
    address owner,
    address spender,
    uint256 value,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) external;
```

### ERC-4626 (Tokenized Vaults)
```solidity
interface IERC4626 {
    function asset() external view returns (address);
    function totalAssets() external view returns (uint256);
    function convertToShares(uint256 assets) external view returns (uint256);
    function convertToAssets(uint256 shares) external view returns (uint256);
    function deposit(uint256 assets, address receiver) external returns (uint256 shares);
    function mint(uint256 shares, address receiver) external returns (uint256 assets);
    function withdraw(uint256 assets, address receiver, address owner) external returns (uint256 shares);
    function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets);
}
```

## NFT Extensions

### ERC-2981 (NFT Royalties)
```solidity
interface IERC2981 {
    function royaltyInfo(uint256 tokenId, uint256 salePrice)
        external
        view
        returns (address receiver, uint256 royaltyAmount);
}
```

### ERC-4907 (Rental NFTs)
```solidity
interface IERC4907 {
    function setUser(uint256 tokenId, address user, uint64 expires) external;
    function userOf(uint256 tokenId) external view returns (address);
    function userExpires(uint256 tokenId) external view returns (uint256);
}
```

### ERC-5192 (Soulbound Tokens)
```solidity
interface IERC5192 {
    function locked(uint256 tokenId) external view returns (bool);
}
```

## Governance Standards

### ERC-2535 (Diamond Pattern)
Upgradeable contracts with multiple facets

### ERC-5805 (Voting)
```solidity
interface IERC5805 {
    function getVotes(address account) external view returns (uint256);
    function getPastVotes(address account, uint256 blockNumber) external view returns (uint256);
    function delegate(address delegatee) external;
}
```

## Metadata Standards

### ERC-721 Metadata
```json
{
  "name": "Asset Name",
  "description": "Description",
  "image": "ipfs://...",
  "attributes": [
    {
      "trait_type": "Rarity",
      "value": "Legendary"
    }
  ]
}
```

### ERC-1155 Metadata
```json
{
  "name": "Asset {id}",
  "description": "Description",
  "image": "ipfs://.../{id}.png",
  "properties": {
    "simple_property": "value"
  }
}
```

## Security Standards

### ERC-165 (Interface Detection)
```solidity
interface IERC165 {
    function supportsInterface(bytes4 interfaceId) external view returns (bool);
}
```

## When to Use Each Standard

| Standard | Use Case |
|----------|----------|
| ERC-20 | Currencies, governance tokens, utility tokens |
| ERC-721 | Unique collectibles, real estate, identity |
| ERC-1155 | Gaming items, multi-class assets |
| ERC-2612 | Gas-less approvals |
| ERC-4626 | Yield vaults, strategies |
| ERC-2981 | NFT royalties |
| ERC-4907 | NFT rentals, time-based access |
| ERC-5192 | Non-transferable credentials |
| ERC-2535 | Complex upgradeable systems |

## Implementation Tips

1. **Always use OpenZeppelin**: Battle-tested implementations
2. **Add extensions carefully**: More features = more complexity
3. **Test thoroughly**: Especially token transfer edge cases
4. **Follow conventions**: Standard naming, events, errors
5. **Document deviations**: If you modify standard behavior

## Quick Reference Links

- EIP Repository: https://eips.ethereum.org
- OpenZeppelin Contracts: https://docs.openzeppelin.com/contracts
- ERC-20: https://eips.ethereum.org/EIPS/eip-20
- ERC-721: https://eips.ethereum.org/EIPS/eip-721
- ERC-1155: https://eips.ethereum.org/EIPS/eip-1155
