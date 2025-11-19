// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title AdvancedNFT
 * @dev Production-ready NFT with comprehensive features:
 * - ERC721 with enumerable and URI storage
 * - ERC2981 royalty standard
 * - Whitelist minting with Merkle proofs
 * - Public minting with limits
 * - Reveal mechanism
 * - Royalty distribution
 * - Metadata management
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

    // Collection configuration
    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MAX_PER_WALLET = 5;
    uint256 public constant WHITELIST_PRICE = 0.05 ether;
    uint256 public constant PUBLIC_PRICE = 0.08 ether;

    // Sale phases
    enum Phase {
        CLOSED,
        WHITELIST,
        PUBLIC
    }

    Phase public currentPhase = Phase.CLOSED;

    // Whitelist
    bytes32 public whitelistMerkleRoot;
    mapping(address => uint256) public whitelistMinted;

    // Public mint tracking
    mapping(address => uint256) public publicMinted;

    // Metadata
    string public baseTokenURI;
    string public notRevealedURI;
    bool public revealed = false;

    // Withdraw addresses
    address public treasury;
    address public artist;

    // Events
    event PhaseChanged(Phase newPhase);
    event Revealed();
    event WhitelistMint(address indexed minter, uint256 quantity);
    event PublicMint(address indexed minter, uint256 quantity);

    constructor(
        string memory _name,
        string memory _symbol,
        string memory _notRevealedURI,
        bytes32 _whitelistRoot,
        address _treasury,
        address _artist
    ) ERC721(_name, _symbol) Ownable(msg.sender) {
        notRevealedURI = _notRevealedURI;
        whitelistMerkleRoot = _whitelistRoot;
        treasury = _treasury;
        artist = _artist;

        // Set default royalty to 5%
        _setDefaultRoyalty(artist, 500); // 500 = 5%
    }

    /**
     * @dev Whitelist mint with Merkle proof
     */
    function whitelistMint(uint256 quantity, bytes32[] calldata proof)
        external
        payable
        nonReentrant
    {
        require(currentPhase == Phase.WHITELIST, "Whitelist phase not active");
        require(totalSupply() + quantity <= MAX_SUPPLY, "Exceeds max supply");
        require(whitelistMinted[msg.sender] + quantity <= MAX_PER_WALLET, "Exceeds wallet limit");
        require(msg.value >= WHITELIST_PRICE * quantity, "Insufficient payment");

        // Verify Merkle proof
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        require(
            MerkleProof.verify(proof, whitelistMerkleRoot, leaf),
            "Invalid proof"
        );

        whitelistMinted[msg.sender] += quantity;

        for (uint256 i = 0; i < quantity; i++) {
            uint256 tokenId = totalSupply() + 1;
            _safeMint(msg.sender, tokenId);
        }

        emit WhitelistMint(msg.sender, quantity);
    }

    /**
     * @dev Public mint
     */
    function publicMint(uint256 quantity) external payable nonReentrant {
        require(currentPhase == Phase.PUBLIC, "Public phase not active");
        require(totalSupply() + quantity <= MAX_SUPPLY, "Exceeds max supply");
        require(publicMinted[msg.sender] + quantity <= MAX_PER_WALLET, "Exceeds wallet limit");
        require(msg.value >= PUBLIC_PRICE * quantity, "Insufficient payment");

        publicMinted[msg.sender] += quantity;

        for (uint256 i = 0; i < quantity; i++) {
            uint256 tokenId = totalSupply() + 1;
            _safeMint(msg.sender, tokenId);
        }

        emit PublicMint(msg.sender, quantity);
    }

    /**
     * @dev Owner mint for team and giveaways
     */
    function ownerMint(address to, uint256 quantity) external onlyOwner {
        require(totalSupply() + quantity <= MAX_SUPPLY, "Exceeds max supply");

        for (uint256 i = 0; i < quantity; i++) {
            uint256 tokenId = totalSupply() + 1;
            _safeMint(to, tokenId);
        }
    }

    /**
     * @dev Set sale phase
     */
    function setPhase(Phase _phase) external onlyOwner {
        currentPhase = _phase;
        emit PhaseChanged(_phase);
    }

    /**
     * @dev Reveal collection
     */
    function reveal(string memory _baseTokenURI) external onlyOwner {
        require(!revealed, "Already revealed");
        baseTokenURI = _baseTokenURI;
        revealed = true;
        emit Revealed();
    }

    /**
     * @dev Update whitelist root
     */
    function setWhitelistRoot(bytes32 _root) external onlyOwner {
        whitelistMerkleRoot = _root;
    }

    /**
     * @dev Set not revealed URI
     */
    function setNotRevealedURI(string memory _uri) external onlyOwner {
        notRevealedURI = _uri;
    }

    /**
     * @dev Set base URI
     */
    function setBaseURI(string memory _uri) external onlyOwner {
        baseTokenURI = _uri;
    }

    /**
     * @dev Update royalty info
     */
    function setDefaultRoyalty(address receiver, uint96 feeNumerator) external onlyOwner {
        _setDefaultRoyalty(receiver, feeNumerator);
    }

    /**
     * @dev Set token-specific royalty
     */
    function setTokenRoyalty(
        uint256 tokenId,
        address receiver,
        uint96 feeNumerator
    ) external onlyOwner {
        _setTokenRoyalty(tokenId, receiver, feeNumerator);
    }

    /**
     * @dev Withdraw funds
     */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");

        // 80% to treasury, 20% to artist
        uint256 artistShare = (balance * 20) / 100;
        uint256 treasuryShare = balance - artistShare;

        (bool successArtist, ) = artist.call{value: artistShare}("");
        require(successArtist, "Artist transfer failed");

        (bool successTreasury, ) = treasury.call{value: treasuryShare}("");
        require(successTreasury, "Treasury transfer failed");
    }

    /**
     * @dev Get token URI
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");

        if (!revealed) {
            return notRevealedURI;
        }

        string memory baseURI = _baseURI();
        return
            bytes(baseURI).length > 0
                ? string(abi.encodePacked(baseURI, tokenId.toString(), ".json"))
                : "";
    }

    /**
     * @dev Get tokens owned by address
     */
    function tokensOfOwner(address owner)
        external
        view
        returns (uint256[] memory)
    {
        uint256 tokenCount = balanceOf(owner);
        uint256[] memory tokenIds = new uint256[](tokenCount);

        for (uint256 i = 0; i < tokenCount; i++) {
            tokenIds[i] = tokenOfOwnerByIndex(owner, i);
        }

        return tokenIds;
    }

    /**
     * @dev Base URI
     */
    function _baseURI() internal view override returns (string memory) {
        return baseTokenURI;
    }

    /**
     * @dev Required overrides
     */
    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Enumerable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, value);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Royalty)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
