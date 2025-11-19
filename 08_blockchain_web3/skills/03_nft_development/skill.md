# NFT Development

## Overview
Build NFT ecosystems including ERC-721/ERC-1155 implementations, marketplaces, metadata management, royalties, and advanced NFT mechanics for gaming, art, and utility applications.

## Core Standards

### 1. ERC-721 (Non-Fungible Token)
- **Unique Identifiers**: Each token has unique ID
- **Ownership Tracking**: Individual ownership per token
- **Transfer Mechanics**: Safe transfer with callback
- **Approval System**: Approve operators for transfers
- **Metadata**: Token URI for off-chain metadata
- **Events**: Transfer, Approval, ApprovalForAll

### 2. ERC-1155 (Multi-Token Standard)
- **Batch Operations**: Transfer multiple token types
- **Fungible + Non-Fungible**: Support both in single contract
- **Gas Efficiency**: Reduced gas costs for batch operations
- **Safe Transfers**: Built-in safe transfer checks
- **Metadata**: URI substitution for token IDs

### 3. ERC-2981 (NFT Royalty Standard)
- **Royalty Information**: On-chain royalty data
- **Sale Price Percentage**: Configurable royalty percentage
- **Recipient Address**: Royalty payment recipient
- **Marketplace Integration**: Standard interface for platforms

## Advanced Features

### 1. Dynamic NFTs
- **On-Chain Metadata**: Store metadata on-chain
- **Trait Evolution**: NFTs that change over time
- **Game Integration**: Stats and attributes
- **Oracle Integration**: Real-world data updates
- **Generative Art**: Procedural generation

### 2. Soulbound Tokens (SBTs)
- **Non-Transferable**: Cannot be sold or transferred
- **Identity Verification**: Proof of achievements
- **Reputation Systems**: On-chain credentials
- **Access Control**: Membership verification

### 3. Programmable Royalties
- **Multi-Recipient**: Split royalties among creators
- **Dynamic Rates**: Change based on conditions
- **Perpetual Royalties**: Enforce across all sales
- **Marketplace Compatibility**: Work with major platforms

### 4. Fractionalization
- **ERC-20 Wrapping**: Convert NFT to fungible tokens
- **Governance Rights**: Vote on NFT decisions
- **Buyout Mechanisms**: Recombine fractions
- **Price Discovery**: Market-driven valuation

## NFT Use Cases

### 1. Digital Art
- Generative art collections
- 1/1 artwork
- Profile picture (PFP) projects
- Interactive art pieces

### 2. Gaming Assets
- In-game items
- Character skins
- Virtual land
- Achievement badges

### 3. Membership & Access
- DAO membership tokens
- Event tickets
- Subscription passes
- Exclusive community access

### 4. Real-World Assets
- Property deeds
- Luxury goods authentication
- Supply chain tracking
- Intellectual property

## Implementation Patterns

### 1. Minting Strategies
```solidity
// Public mint with limit
function publicMint(uint256 quantity) external payable {
    require(totalSupply() + quantity <= MAX_SUPPLY);
    require(msg.value >= MINT_PRICE * quantity);
    require(quantity <= MAX_PER_TX);

    _mint(msg.sender, quantity);
}

// Whitelist mint
function whitelistMint(bytes32[] calldata proof) external {
    require(_verifyWhitelist(msg.sender, proof));
    require(!whitelistClaimed[msg.sender]);

    whitelistClaimed[msg.sender] = true;
    _mint(msg.sender, 1);
}

// Dutch auction
function dutchAuctionMint() external payable {
    uint256 currentPrice = getCurrentPrice();
    require(msg.value >= currentPrice);

    _mint(msg.sender, 1);

    // Refund excess
    if (msg.value > currentPrice) {
        payable(msg.sender).transfer(msg.value - currentPrice);
    }
}
```

### 2. Metadata Management
```solidity
// IPFS metadata
string baseURI = "ipfs://QmHash/";

function tokenURI(uint256 tokenId)
    public view returns (string memory)
{
    return string(abi.encodePacked(baseURI, tokenId.toString(), ".json"));
}

// On-chain metadata
struct Metadata {
    string name;
    string description;
    uint256[] traits;
}

mapping(uint256 => Metadata) public tokenMetadata;

// Dynamic metadata
function updateMetadata(uint256 tokenId, uint256[] memory newTraits)
    external onlyOwner
{
    tokenMetadata[tokenId].traits = newTraits;
    emit MetadataUpdate(tokenId);
}
```

### 3. Reveal Mechanics
```solidity
// Delayed reveal
bool public revealed = false;
string public notRevealedURI;
string public baseURI;

function tokenURI(uint256 tokenId) public view returns (string memory) {
    if (!revealed) {
        return notRevealedURI;
    }
    return string(abi.encodePacked(baseURI, tokenId.toString()));
}

function reveal(string memory _baseURI) external onlyOwner {
    baseURI = _baseURI;
    revealed = true;
}
```

## Security Best Practices

### 1. Reentrancy Protection
- Use ReentrancyGuard for payable functions
- Follow checks-effects-interactions pattern
- Use pull payment patterns for withdrawals

### 2. Access Control
- Implement proper owner controls
- Role-based permissions for operators
- Timelock for critical functions

### 3. Supply Management
- Enforce max supply limits
- Prevent unauthorized minting
- Track circulating supply accurately

### 4. Metadata Security
- Immutable IPFS storage
- Verify metadata hash on-chain
- Protect against URI manipulation

## Gas Optimization

### 1. Storage Optimization
```solidity
// Pack variables
struct TokenData {
    address owner;          // 20 bytes
    uint64 mintTimestamp;  // 8 bytes
    uint32 lastTransfer;   // 4 bytes
}

// Use mappings efficiently
mapping(uint256 => TokenData) private _tokenData;
```

### 2. Batch Operations
```solidity
// Batch mint
function batchMint(address[] calldata recipients, uint256[] calldata quantities)
    external onlyOwner
{
    require(recipients.length == quantities.length);

    for (uint256 i = 0; i < recipients.length; i++) {
        _mint(recipients[i], quantities[i]);
    }
}
```

### 3. ERC721A Pattern
- Sequential minting optimization
- Batch mint gas savings
- Lazy initialization of ownership

## Marketplace Integration

### 1. OpenSea Compatibility
```solidity
function contractURI() public view returns (string memory) {
    return _contractURI;
}

function setApprovalForAll(address operator, bool approved) public override {
    // OpenSea proxy integration
    super.setApprovalForAll(operator, approved);
}
```

### 2. Royalty Implementation
```solidity
function royaltyInfo(uint256 tokenId, uint256 salePrice)
    external view returns (address receiver, uint256 royaltyAmount)
{
    return (royaltyReceiver, (salePrice * royaltyBps) / 10000);
}
```

## Testing Strategies

### Unit Tests
```javascript
describe("NFT Contract", function() {
    it("Should mint NFT correctly", async function() {
        const tx = await nft.mint(user.address);
        await expect(tx)
            .to.emit(nft, "Transfer")
            .withArgs(ethers.ZeroAddress, user.address, 1);

        expect(await nft.ownerOf(1)).to.equal(user.address);
    });

    it("Should respect max supply", async function() {
        // Mint to max supply
        await nft.mint(MAX_SUPPLY);

        // Next mint should fail
        await expect(nft.mint(1)).to.be.revertedWith("Max supply reached");
    });
});
```

## Resources

### Standards
- EIP-721: Non-Fungible Token Standard
- EIP-1155: Multi-Token Standard
- EIP-2981: NFT Royalty Standard
- EIP-4907: Rental NFT Standard
- EIP-5192: Minimal Soulbound NFT

### Tools
- OpenZeppelin Contracts
- ERC721A (Azuki)
- Manifold Creator Tools
- NFT Port API
- Pinata (IPFS)

### Marketplaces
- OpenSea
- Rarible
- LooksRare
- Blur
- Foundation

## Conclusion

NFT development combines smart contract engineering, metadata management, and user experience design. Focus on security, gas efficiency, and standards compliance for successful NFT projects.
