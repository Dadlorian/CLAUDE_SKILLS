# ERC Standards Reference

## What are ERC Standards?

ERC (Ethereum Request for Comments) standards are specifications for smart contracts on Ethereum. They define interfaces and behaviors that contracts must follow, enabling interoperability.

### Standard Process
1. **Draft**: Initial proposal (EIP-X)
2. **Review**: Community discussion and feedback
3. **Final**: Accepted and implemented
4. **Superseded**: New version replaces old (if applicable)

## ERC-20: Token Standard

### Purpose
Standard interface for fungible tokens (interchangeable, same value).

### Required Functions
```solidity
// Get account balance
function balanceOf(address account) public view returns (uint256);

// Total token supply
function totalSupply() public view returns (uint256);

// Transfer tokens
function transfer(address to, uint256 amount) public returns (bool);

// Transfer from account (requires approval)
function transferFrom(address from, address to, uint256 amount)
  public returns (bool);

// Allow spender to use tokens
function approve(address spender, uint256 amount) public returns (bool);

// Check allowance
function allowance(address owner, address spender)
  public view returns (uint256);
```

### Required Events
```solidity
event Transfer(address indexed from, address indexed to, uint256 value);
event Approval(address indexed owner, address indexed spender, uint256 value);
```

### Common Extensions
```solidity
// IERC20Metadata
function name() public view returns (string);
function symbol() public view returns (string);
function decimals() public view returns (uint8);
```

### Implementation Example
```solidity
contract MyToken is IERC20 {
  mapping(address => uint256) balances;
  mapping(address => mapping(address => uint256)) allowances;
  uint256 public totalSupply;
  string public name = "My Token";
  string public symbol = "MTK";
  uint8 public decimals = 18;

  function balanceOf(address account) public view returns (uint256) {
    return balances[account];
  }

  function transfer(address to, uint256 amount) public returns (bool) {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    balances[to] += amount;
    emit Transfer(msg.sender, to, amount);
    return true;
  }

  function approve(address spender, uint256 amount) public returns (bool) {
    allowances[msg.sender][spender] = amount;
    emit Approval(msg.sender, spender, amount);
    return true;
  }

  function transferFrom(address from, address to, uint256 amount)
    public returns (bool) {
    require(allowances[from][msg.sender] >= amount);
    allowances[from][msg.sender] -= amount;
    balances[from] -= amount;
    balances[to] += amount;
    emit Transfer(from, to, amount);
    return true;
  }

  function allowance(address owner, address spender)
    public view returns (uint256) {
    return allowances[owner][spender];
  }
}
```

## ERC-721: Non-Fungible Token (NFT) Standard

### Purpose
Standard for non-fungible tokens (unique, not interchangeable).

### Required Functions
```solidity
function ownerOf(uint256 tokenId) public view returns (address owner);
function balanceOf(address owner) public view returns (uint256 balance);
function transferFrom(address from, address to, uint256 tokenId) public;
function safeTransferFrom(address from, address to, uint256 tokenId) public;
function approve(address to, uint256 tokenId) public;
function setApprovalForAll(address operator, bool _approved) public;
function getApproved(uint256 tokenId) public view returns (address operator);
function isApprovedForAll(address owner, address operator)
  public view returns (bool);
```

### Required Events
```solidity
event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
event ApprovalForAll(address indexed owner, address indexed operator, bool approved);
```

### Metadata Extension (ERC721Metadata)
```solidity
function name() public view returns (string _name);
function symbol() public view returns (string _symbol);
function tokenURI(uint256 _tokenId) public view returns (string);
```

### Use Cases
- Digital art and collectibles
- Gaming assets
- Domain names
- Real estate deeds
- Certificates and credentials

## ERC-1155: Multi-Token Standard

### Purpose
Single contract manages multiple token types (fungible and non-fungible).

### Key Advantage
```
ERC-20: Each token type needs separate contract
ERC-721: Each NFT collection needs separate contract
ERC-1155: All tokens in single contract
```

### Functions
```solidity
function balanceOf(address account, uint256 id)
  public view returns (uint256);

function balanceOfBatch(address[] calldata accounts, uint256[] calldata ids)
  public view returns (uint256[] memory);

function setApprovalForAll(address operator, bool approved) public;

function isApprovedForAll(address account, address operator)
  public view returns (bool);

function safeTransferFrom(
  address from,
  address to,
  uint256 id,
  uint256 amount,
  bytes calldata data
) public;

function safeBatchTransferFrom(
  address from,
  address to,
  uint256[] calldata ids,
  uint256[] calldata amounts,
  bytes calldata data
) public;
```

### Events
```solidity
event TransferSingle(
  address indexed operator,
  address indexed from,
  address indexed to,
  uint256 id,
  uint256 value
);

event TransferBatch(
  address indexed operator,
  address indexed from,
  address indexed to,
  uint256[] ids,
  uint256[] values
);

event ApprovalForAll(address indexed account, address indexed operator, bool approved);
event URI(string value, uint256 indexed id);
```

## ERC-165: Standard Interface Detection

### Purpose
Contracts declare which interfaces they implement.

### Implementation
```solidity
interface IERC165 {
  function supportsInterface(bytes4 interfaceId) external view returns (bool);
}

contract MyContract is IERC165 {
  function supportsInterface(bytes4 interfaceId)
    public view override returns (bool) {
    return interfaceId == type(IERC165).interfaceId ||
           interfaceId == type(IERC721).interfaceId;
  }
}
```

## ERC-2612: Permit (Signature-Based Approval)

### Purpose
Allows ERC20 approval via signature instead of separate transaction.

### Functions
```solidity
function permit(
  address owner,
  address spender,
  uint256 value,
  uint256 deadline,
  uint8 v,
  bytes32 r,
  bytes32 s
) public;
```

### Benefits
```
Reduces transactions: No separate approve() call needed
UX improvement: Single transaction for transfer
Gas savings: Combined into one transaction
```

## ERC-3156: Flash Loan Receiver

### Purpose
Standard interface for flash loan callbacks.

### Implementation
```solidity
interface IERC3156FlashBorrower {
  function onFlashLoan(
    address initiator,
    address token,
    uint256 amount,
    uint256 fee,
    bytes calldata data
  ) external returns (bytes32);
}
```

## ERC-4626: Tokenized Vault Standard

### Purpose
Standard for yield-bearing vaults.

### Functions
```solidity
function deposit(uint256 assets, address receiver)
  public returns (uint256 shares);

function mint(uint256 shares, address receiver)
  public returns (uint256 assets);

function withdraw(uint256 assets, address receiver, address owner)
  public returns (uint256 shares);

function redeem(uint256 shares, address receiver, address owner)
  public returns (uint256 assets);

// View functions
function totalAssets() public view returns (uint256);
function convertToAssets(uint256 shares) public view returns (uint256);
function convertToShares(uint256 assets) public view returns (uint256);
```

### Benefits
- Standardized vault interface
- Composability with other protocols
- Predictable share/asset conversion
- Enables yield optimizer composability

## ERC-2981: NFT Royalties

### Purpose
Standardize royalty payments for NFT creators.

### Implementation
```solidity
interface IERC2981 {
  function royaltyInfo(uint256 _tokenId, uint256 _salePrice)
    external view returns (address receiver, uint256 royaltyAmount);
}

contract MyNFT is ERC721, IERC2981 {
  function royaltyInfo(uint256 _tokenId, uint256 _salePrice)
    public view override returns (address receiver, uint256 royaltyAmount) {
    royaltyAmount = (_salePrice * 10) / 100;  // 10% royalty
    receiver = owner();
  }
}
```

## ERC-777: Advanced Token Standard

### Purpose
Improve upon ERC-20 with hooks and better usability.

### Features
```
- Tokens and ether handled consistently
- Hooks before/after token movements
- No separate approve() needed
```

### Downside
```
- More complex implementation
- Potential security issues if hooks not carefully designed
- Less widely adopted than ERC-20
```

## ERC-1271: Standard Signature Validation

### Purpose
Smart contracts can verify signatures on behalf of addresses.

### Implementation
```solidity
interface IERC1271 {
  function isValidSignature(bytes32 hash, bytes memory signature)
    external view returns (bytes4 magicValue);
}
```

### Use Case
```
Multisig wallets
Contract-based account abstraction
Smart account authentication
```

## Other Important Standards

### ERC-3668: Off-Chain Data Retrieval
- Enables contracts to reference off-chain data
- Reduces on-chain storage

### ERC-4337: Account Abstraction
- Smart contract accounts
- Meta transactions
- Batched operations

### ERC-1967: Proxy Pattern
- Standard for proxy implementations
- Storage slots for proxy data

### ERC-6902: RLP Encoding
- Recursive Length Prefix encoding
- Data serialization standard

## Version Considerations

### Solidity Version Compatibility
```
Some standards work better with:
- Solidity 0.6.x: Early standards
- Solidity 0.8.x: Custom errors (gas efficient)
- Solidity 0.8.4+: ERC-721A optimizations
```

### OpenZeppelin Contracts
Most widely used ERC implementations:
- Audited code
- Gas optimized
- Well-maintained
- Community standard

```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
```

## Interaction Patterns

### Token Approval Pattern
```solidity
// User approves spender to use tokens
token.approve(spender, amount);

// Spender uses tokens
token.transferFrom(user, recipient, amount);
```

### NFT Transfer Pattern
```solidity
// Approve operator for single NFT
nft.approve(operator, tokenId);

// Or approve for all
nft.setApprovalForAll(operator, true);

// Operator transfers
nft.transferFrom(owner, recipient, tokenId);
```

---

**Key Takeaways**:
- ERC standards enable interoperability
- ERC-20 for fungible tokens
- ERC-721 for unique NFTs
- ERC-1155 for mixed token types
- Standards are battle-tested and widely adopted
- Use OpenZeppelin implementations for production
