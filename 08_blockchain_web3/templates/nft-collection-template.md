# NFT Collection Development Template

Production-ready templates for building secure, gas-optimized NFT collections with advanced features.

## Advanced ERC-721 NFT Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

/**
 * @title AdvancedNFT
 * @notice Production-grade NFT collection with comprehensive features
 * @dev Includes:
 * - ERC-721 with enumeration
 * - ERC-2981 royalties
 * - Allowlist (Merkle tree)
 * - Reveal mechanism
 * - Dynamic metadata
 * - Batch minting
 * - Staking integration hooks
 */
contract AdvancedNFT is
    ERC721,
    ERC721Enumerable,
    ERC721URIStorage,
    ERC721Royalty,
    Ownable,
    ReentrancyGuard
{
    using Strings for uint256;

    /*//////////////////////////////////////////////////////////////
                            STATE VARIABLES
    //////////////////////////////////////////////////////////////*/

    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MAX_PER_WALLET = 5;
    uint256 public constant ALLOWLIST_PRICE = 0.05 ether;
    uint256 public constant PUBLIC_PRICE = 0.08 ether;

    uint256 public currentTokenId;
    bool public isRevealed;
    bool public allowlistMintEnabled;
    bool public publicMintEnabled;

    string private baseTokenURI;
    string private unrevealedURI;
    bytes32 public merkleRoot;

    mapping(address => uint256) public mintedPerWallet;
    mapping(uint256 => TokenMetadata) public tokenMetadata;

    struct TokenMetadata {
        uint8 rarity;        // 1-5
        uint16 level;
        uint32 experience;
        bool isStaked;
    }

    /*//////////////////////////////////////////////////////////////
                                EVENTS
    //////////////////////////////////////////////////////////////*/

    event Minted(address indexed to, uint256 indexed tokenId, uint256 quantity);
    event Revealed(string baseURI);
    event MetadataUpdated(uint256 indexed tokenId, TokenMetadata metadata);
    event Staked(uint256 indexed tokenId);
    event Unstaked(uint256 indexed tokenId);

    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error MaxSupplyReached();
    error MaxPerWalletReached();
    error InsufficientPayment();
    error InvalidProof();
    error MintNotEnabled();
    error TokenNotFound();
    error AlreadyRevealed();

    /*//////////////////////////////////////////////////////////////
                            CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(
        string memory name,
        string memory symbol,
        string memory _unrevealedURI,
        bytes32 _merkleRoot
    ) ERC721(name, symbol) {
        unrevealedURI = _unrevealedURI;
        merkleRoot = _merkleRoot;

        // Set default royalty to 5%
        _setDefaultRoyalty(msg.sender, 500);
    }

    /*//////////////////////////////////////////////////////////////
                            MINTING LOGIC
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Allowlist mint with Merkle proof
     * @param quantity Number of NFTs to mint
     * @param merkleProof Merkle proof for allowlist
     */
    function allowlistMint(uint256 quantity, bytes32[] calldata merkleProof)
        external
        payable
        nonReentrant
    {
        if (!allowlistMintEnabled) revert MintNotEnabled();
        if (currentTokenId + quantity > MAX_SUPPLY) revert MaxSupplyReached();
        if (mintedPerWallet[msg.sender] + quantity > MAX_PER_WALLET) revert MaxPerWalletReached();
        if (msg.value < ALLOWLIST_PRICE * quantity) revert InsufficientPayment();

        // Verify Merkle proof
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        if (!MerkleProof.verify(merkleProof, merkleRoot, leaf)) revert InvalidProof();

        _batchMint(msg.sender, quantity);
    }

    /**
     * @notice Public mint
     * @param quantity Number of NFTs to mint
     */
    function publicMint(uint256 quantity) external payable nonReentrant {
        if (!publicMintEnabled) revert MintNotEnabled();
        if (currentTokenId + quantity > MAX_SUPPLY) revert MaxSupplyReached();
        if (mintedPerWallet[msg.sender] + quantity > MAX_PER_WALLET) revert MaxPerWalletReached();
        if (msg.value < PUBLIC_PRICE * quantity) revert InsufficientPayment();

        _batchMint(msg.sender, quantity);
    }

    /**
     * @notice Owner mint for team/marketing
     * @param to Recipient address
     * @param quantity Number of NFTs to mint
     */
    function ownerMint(address to, uint256 quantity) external onlyOwner {
        if (currentTokenId + quantity > MAX_SUPPLY) revert MaxSupplyReached();
        _batchMint(to, quantity);
    }

    /**
     * @dev Internal batch minting function
     */
    function _batchMint(address to, uint256 quantity) internal {
        uint256 startTokenId = currentTokenId;

        for (uint256 i = 0; i < quantity; i++) {
            uint256 tokenId = currentTokenId++;
            _safeMint(to, tokenId);

            // Generate pseudo-random attributes
            // Note: This is deterministic; use Chainlink VRF for true randomness
            _generateMetadata(tokenId);
        }

        mintedPerWallet[to] += quantity;
        emit Minted(to, startTokenId, quantity);
    }

    /**
     * @dev Generate metadata for a token
     */
    function _generateMetadata(uint256 tokenId) internal {
        // Pseudo-random rarity (use Chainlink VRF in production)
        uint256 randomness = uint256(
            keccak256(abi.encodePacked(block.timestamp, block.prevrandao, tokenId))
        );

        uint8 rarity;
        uint256 rarityRoll = randomness % 100;

        if (rarityRoll < 1) {
            rarity = 5; // Legendary - 1%
        } else if (rarityRoll < 6) {
            rarity = 4; // Epic - 5%
        } else if (rarityRoll < 21) {
            rarity = 3; // Rare - 15%
        } else if (rarityRoll < 51) {
            rarity = 2; // Uncommon - 30%
        } else {
            rarity = 1; // Common - 49%
        }

        tokenMetadata[tokenId] = TokenMetadata({
            rarity: rarity,
            level: 1,
            experience: 0,
            isStaked: false
        });
    }

    /*//////////////////////////////////////////////////////////////
                            REVEAL LOGIC
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Reveal collection
     * @param _baseTokenURI Base URI for revealed metadata
     */
    function reveal(string memory _baseTokenURI) external onlyOwner {
        if (isRevealed) revert AlreadyRevealed();
        baseTokenURI = _baseTokenURI;
        isRevealed = true;
        emit Revealed(_baseTokenURI);
    }

    /**
     * @notice Get token URI
     * @param tokenId Token ID
     * @return Token URI
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        if (!_exists(tokenId)) revert TokenNotFound();

        if (!isRevealed) {
            return unrevealedURI;
        }

        TokenMetadata memory metadata = tokenMetadata[tokenId];

        // Return dynamic URI based on metadata
        return
            string(
                abi.encodePacked(
                    baseTokenURI,
                    tokenId.toString(),
                    "?rarity=",
                    uint256(metadata.rarity).toString(),
                    "&level=",
                    uint256(metadata.level).toString()
                )
            );
    }

    /*//////////////////////////////////////////////////////////////
                        STAKING INTEGRATION
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Stake NFT (callable by staking contract)
     * @param tokenId Token ID
     */
    function stake(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        tokenMetadata[tokenId].isStaked = true;
        emit Staked(tokenId);
    }

    /**
     * @notice Unstake NFT (callable by staking contract)
     * @param tokenId Token ID
     */
    function unstake(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        tokenMetadata[tokenId].isStaked = false;
        emit Unstaked(tokenId);
    }

    /**
     * @notice Update token experience/level (callable by game contract)
     * @param tokenId Token ID
     * @param experience New experience value
     */
    function updateExperience(uint256 tokenId, uint32 experience) external {
        // In production, add access control for game contract
        require(ownerOf(tokenId) != address(0), "Token doesn't exist");

        tokenMetadata[tokenId].experience = experience;

        // Auto-level up logic
        uint16 newLevel = uint16(experience / 1000) + 1;
        if (newLevel > tokenMetadata[tokenId].level) {
            tokenMetadata[tokenId].level = newLevel;
        }

        emit MetadataUpdated(tokenId, tokenMetadata[tokenId]);
    }

    /*//////////////////////////////////////////////////////////////
                        ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Set base URI
     */
    function setBaseURI(string memory _baseTokenURI) external onlyOwner {
        baseTokenURI = _baseTokenURI;
    }

    /**
     * @notice Set unrevealed URI
     */
    function setUnrevealedURI(string memory _unrevealedURI) external onlyOwner {
        unrevealedURI = _unrevealedURI;
    }

    /**
     * @notice Set Merkle root for allowlist
     */
    function setMerkleRoot(bytes32 _merkleRoot) external onlyOwner {
        merkleRoot = _merkleRoot;
    }

    /**
     * @notice Toggle allowlist mint
     */
    function toggleAllowlistMint() external onlyOwner {
        allowlistMintEnabled = !allowlistMintEnabled;
    }

    /**
     * @notice Toggle public mint
     */
    function togglePublicMint() external onlyOwner {
        publicMintEnabled = !publicMintEnabled;
    }

    /**
     * @notice Update royalty info
     */
    function setRoyaltyInfo(address receiver, uint96 feeNumerator) external onlyOwner {
        _setDefaultRoyalty(receiver, feeNumerator);
    }

    /**
     * @notice Withdraw funds
     */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "Withdrawal failed");
    }

    /*//////////////////////////////////////////////////////////////
                        OVERRIDE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        // Prevent transfer while staked
        if (from != address(0)) {
            require(!tokenMetadata[tokenId].isStaked, "Token is staked");
        }
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage, ERC721Royalty) {
        super._burn(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721Royalty)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

## ERC-1155 Multi-Token Template

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title GameAssets
 * @notice ERC-1155 for game assets, items, and currencies
 * @dev Supports:
 * - Multiple token types (fungible + non-fungible)
 * - Crafting/burning mechanics
 * - In-game currency
 * - Batch operations
 */
contract GameAssets is ERC1155, ERC1155Supply, Ownable, ReentrancyGuard {
    string public name = "Game Assets";
    string public symbol = "GAME";

    uint256 public constant GOLD = 0;           // Fungible
    uint256 public constant WOOD = 1;           // Fungible
    uint256 public constant STONE = 2;          // Fungible
    uint256 public constant SWORD_COMMON = 100; // Semi-fungible
    uint256 public constant SWORD_RARE = 101;   // Semi-fungible
    uint256 public constant LAND_NFT = 1000;    // Non-fungible (supply = 1 each)

    mapping(uint256 => uint256) public maxSupply;
    mapping(uint256 => bool) public isFungible;
    mapping(uint256 => string) public tokenURIs;

    // Crafting recipes
    struct Recipe {
        uint256[] inputs;
        uint256[] inputAmounts;
        uint256 output;
        uint256 outputAmount;
    }

    mapping(uint256 => Recipe) public recipes;

    event Crafted(address indexed player, uint256 recipeId, uint256 amount);
    event TokenTypeCreated(uint256 indexed tokenId, bool fungible, uint256 maxSupply);

    constructor() ERC1155("https://game.example/api/item/{id}.json") {}

    /**
     * @notice Create new token type
     */
    function createTokenType(
        uint256 tokenId,
        bool _isFungible,
        uint256 _maxSupply,
        string memory _tokenURI
    ) external onlyOwner {
        require(maxSupply[tokenId] == 0, "Token type exists");

        maxSupply[tokenId] = _maxSupply;
        isFungible[tokenId] = _isFungible;
        tokenURIs[tokenId] = _tokenURI;

        emit TokenTypeCreated(tokenId, _isFungible, _maxSupply);
    }

    /**
     * @notice Mint tokens
     */
    function mint(
        address to,
        uint256 tokenId,
        uint256 amount
    ) external onlyOwner {
        require(
            totalSupply(tokenId) + amount <= maxSupply[tokenId],
            "Exceeds max supply"
        );

        _mint(to, tokenId, amount, "");
    }

    /**
     * @notice Batch mint
     */
    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) external onlyOwner {
        for (uint256 i = 0; i < ids.length; i++) {
            require(
                totalSupply(ids[i]) + amounts[i] <= maxSupply[ids[i]],
                "Exceeds max supply"
            );
        }

        _mintBatch(to, ids, amounts, "");
    }

    /**
     * @notice Craft items using recipe
     * @param recipeId Recipe ID
     * @param amount Number of times to craft
     */
    function craft(uint256 recipeId, uint256 amount) external nonReentrant {
        Recipe memory recipe = recipes[recipeId];
        require(recipe.output != 0, "Invalid recipe");

        // Burn inputs
        for (uint256 i = 0; i < recipe.inputs.length; i++) {
            _burn(msg.sender, recipe.inputs[i], recipe.inputAmounts[i] * amount);
        }

        // Mint output
        _mint(msg.sender, recipe.output, recipe.outputAmount * amount, "");

        emit Crafted(msg.sender, recipeId, amount);
    }

    /**
     * @notice Set crafting recipe
     */
    function setRecipe(
        uint256 recipeId,
        uint256[] memory inputs,
        uint256[] memory inputAmounts,
        uint256 output,
        uint256 outputAmount
    ) external onlyOwner {
        require(inputs.length == inputAmounts.length, "Length mismatch");

        recipes[recipeId] = Recipe({
            inputs: inputs,
            inputAmounts: inputAmounts,
            output: output,
            outputAmount: outputAmount
        });
    }

    /**
     * @notice Get token URI
     */
    function uri(uint256 tokenId) public view override returns (string memory) {
        return tokenURIs[tokenId];
    }

    function _beforeTokenTransfer(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) internal override(ERC1155, ERC1155Supply) {
        super._beforeTokenTransfer(operator, from, to, ids, amounts, data);
    }
}
```

## NFT Staking Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title NFTStaking
 * @notice Stake NFTs to earn ERC-20 rewards
 */
contract NFTStaking is ReentrancyGuard, Ownable {
    IERC721 public immutable nftCollection;
    IERC20 public immutable rewardToken;

    uint256 public rewardRate = 100 ether; // Tokens per day per NFT

    struct Stake {
        address owner;
        uint256 timestamp;
    }

    mapping(uint256 => Stake) public stakes;
    mapping(address => uint256[]) public stakedTokens;

    event Staked(address indexed user, uint256 indexed tokenId);
    event Unstaked(address indexed user, uint256 indexed tokenId);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor(address _nftCollection, address _rewardToken) {
        nftCollection = IERC721(_nftCollection);
        rewardToken = IERC20(_rewardToken);
    }

    /**
     * @notice Stake NFT
     */
    function stake(uint256 tokenId) external nonReentrant {
        nftCollection.transferFrom(msg.sender, address(this), tokenId);

        stakes[tokenId] = Stake({owner: msg.sender, timestamp: block.timestamp});

        stakedTokens[msg.sender].push(tokenId);

        emit Staked(msg.sender, tokenId);
    }

    /**
     * @notice Unstake NFT and claim rewards
     */
    function unstake(uint256 tokenId) external nonReentrant {
        require(stakes[tokenId].owner == msg.sender, "Not owner");

        // Calculate and send rewards
        uint256 reward = calculateReward(tokenId);
        if (reward > 0) {
            rewardToken.transfer(msg.sender, reward);
            emit RewardClaimed(msg.sender, reward);
        }

        // Return NFT
        nftCollection.transferFrom(address(this), msg.sender, tokenId);

        // Remove from staked tokens
        _removeFromStakedTokens(msg.sender, tokenId);
        delete stakes[tokenId];

        emit Unstaked(msg.sender, tokenId);
    }

    /**
     * @notice Claim rewards without unstaking
     */
    function claimRewards(uint256 tokenId) external nonReentrant {
        require(stakes[tokenId].owner == msg.sender, "Not owner");

        uint256 reward = calculateReward(tokenId);
        require(reward > 0, "No rewards");

        stakes[tokenId].timestamp = block.timestamp;
        rewardToken.transfer(msg.sender, reward);

        emit RewardClaimed(msg.sender, reward);
    }

    /**
     * @notice Calculate pending rewards
     */
    function calculateReward(uint256 tokenId) public view returns (uint256) {
        Stake memory stakeInfo = stakes[tokenId];
        if (stakeInfo.owner == address(0)) return 0;

        uint256 stakingTime = block.timestamp - stakeInfo.timestamp;
        return (stakingTime * rewardRate) / 1 days;
    }

    /**
     * @notice Get all staked tokens for user
     */
    function getStakedTokens(address user) external view returns (uint256[] memory) {
        return stakedTokens[user];
    }

    /**
     * @dev Remove token from stakedTokens array
     */
    function _removeFromStakedTokens(address user, uint256 tokenId) internal {
        uint256[] storage tokens = stakedTokens[user];
        for (uint256 i = 0; i < tokens.length; i++) {
            if (tokens[i] == tokenId) {
                tokens[i] = tokens[tokens.length - 1];
                tokens.pop();
                break;
            }
        }
    }

    /**
     * @notice Update reward rate (owner only)
     */
    function setRewardRate(uint256 _rewardRate) external onlyOwner {
        rewardRate = _rewardRate;
    }

    /**
     * @notice Emergency withdraw rewards (owner only)
     */
    function emergencyWithdrawRewards() external onlyOwner {
        uint256 balance = rewardToken.balanceOf(address(this));
        rewardToken.transfer(owner(), balance);
    }
}
```

## Frontend Integration Example

```typescript
// React + wagmi example
import { useContractWrite, useContractRead } from 'wagmi';
import { parseEther } from 'viem';

function NFTMint() {
  const { data: currentSupply } = useContractRead({
    address: NFT_ADDRESS,
    abi: NFT_ABI,
    functionName: 'currentTokenId',
    watch: true,
  });

  const { write: mint, isLoading } = useContractWrite({
    address: NFT_ADDRESS,
    abi: NFT_ABI,
    functionName: 'publicMint',
    value: parseEther('0.08'),
    args: [1], // quantity
    onSuccess: (data) => {
      toast.success(`Minted! Transaction: ${data.hash}`);
    },
  });

  return (
    <div>
      <p>Minted: {currentSupply?.toString()} / 10000</p>
      <button onClick={() => mint()} disabled={isLoading}>
        {isLoading ? 'Minting...' : 'Mint NFT (0.08 ETH)'}
      </button>
    </div>
  );
}
```

## Testing NFT Contracts

```solidity
contract AdvancedNFTTest is Test {
    AdvancedNFT nft;
    address alice = makeAddr("alice");
    bytes32 merkleRoot;

    function setUp() public {
        // Generate Merkle tree (simplified)
        bytes32[] memory leaves = new bytes32[](1);
        leaves[0] = keccak256(abi.encodePacked(alice));
        merkleRoot = leaves[0];

        nft = new AdvancedNFT("Test NFT", "TEST", "ipfs://unrevealed/", merkleRoot);
        nft.toggleAllowlistMint();
    }

    function test_AllowlistMint() public {
        bytes32[] memory proof = new bytes32[](0);

        vm.deal(alice, 1 ether);
        vm.prank(alice);
        nft.allowlistMint{value: 0.05 ether}(1, proof);

        assertEq(nft.balanceOf(alice), 1);
    }

    function test_Reveal() public {
        nft.reveal("ipfs://revealed/");
        assertTrue(nft.isRevealed());
    }

    function testFuzz_Mint(uint8 quantity) public {
        vm.assume(quantity > 0 && quantity <= 5);

        nft.togglePublicMint();
        vm.deal(alice, 10 ether);
        vm.prank(alice);
        nft.publicMint{value: 0.08 ether * quantity}(quantity);

        assertEq(nft.balanceOf(alice), quantity);
    }
}
```

## Gas Optimization Tips for NFTs

1. **Use ERC721A** for batch minting (saves 50%+ gas)
2. **Avoid ERC721Enumerable** if not needed (expensive)
3. **Pack metadata** into structs
4. **Use bitmap** for tracking mints
5. **Minimize storage writes**
6. **Batch reveal** instead of per-token
7. **Use Merkle trees** for allowlists
8. **Optimize loops** in batch operations

## Security Checklist

- [ ] Reentrancy guards on payable functions
- [ ] Max supply cannot be exceeded
- [ ] Max per wallet enforced
- [ ] Proper access control
- [ ] Merkle proof validation
- [ ] Withdrawal function secure
- [ ] Royalty enforcement (if using marketplaces)
- [ ] Metadata cannot be changed maliciously
- [ ] Transfer restrictions while staked
- [ ] Emergency pause mechanism

## IPFS Metadata Structure

```json
{
  "name": "NFT #1",
  "description": "Collection description",
  "image": "ipfs://QmHash/1.png",
  "attributes": [
    {
      "trait_type": "Rarity",
      "value": "Legendary"
    },
    {
      "trait_type": "Level",
      "value": 1,
      "display_type": "number"
    },
    {
      "trait_type": "Power",
      "value": 95,
      "max_value": 100
    }
  ]
}
```
