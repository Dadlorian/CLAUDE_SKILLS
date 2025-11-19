# NFT Finance Guide

## NFT as Collateral

### NFT Lending Pools
```solidity
contract NFTLendingPool {
    mapping(address => mapping(uint256 => address)) public nftDeposits;
    mapping(address => uint256) public borrowLimit;

    function depositNFT(address nftAddress, uint256 tokenId) external {
        IERC721(nftAddress).transferFrom(msg.sender, address(this), tokenId);
        nftDeposits[nftAddress][tokenId] = msg.sender;
        borrowLimit[msg.sender] += getNFTValue(nftAddress, tokenId);
    }

    function borrowAgainstNFT(uint256 amount) external {
        require(amount <= borrowLimit[msg.sender], "Exceeds limit");
        // Transfer loan amount
        stablecoin.transfer(msg.sender, amount);
    }

    function withdrawNFT(address nftAddress, uint256 tokenId) external {
        require(nftDeposits[nftAddress][tokenId] == msg.sender, "Not owner");
        IERC721(nftAddress).safeTransferFrom(address(this), msg.sender, tokenId);
        delete nftDeposits[nftAddress][tokenId];
    }
}
```

## NFT-Backed Loans

### Auction-Based Liquidation
```solidity
contract NFTAuction {
    struct Auction {
        address nft;
        uint256 tokenId;
        uint256 startPrice;
        uint256 endTime;
        address highestBidder;
        uint256 highestBid;
        bool settled;
    }

    mapping(uint256 => Auction) public auctions;

    function placeBid(uint256 auctionId, uint256 amount) external {
        Auction storage auction = auctions[auctionId];
        require(block.timestamp < auction.endTime, "Auction ended");
        require(amount > auction.highestBid, "Bid too low");

        // Refund previous bid
        if (auction.highestBidder != address(0)) {
            IERC20(stablecoin).transfer(auction.highestBidder, auction.highestBid);
        }

        auction.highestBidder = msg.sender;
        auction.highestBid = amount;
    }

    function settleAuction(uint256 auctionId) external {
        Auction storage auction = auctions[auctionId];
        require(block.timestamp >= auction.endTime, "Auction ongoing");
        require(!auction.settled, "Already settled");

        auction.settled = true;

        // Transfer NFT to winner
        IERC721(auction.nft).safeTransferFrom(
            address(this),
            auction.highestBidder,
            auction.tokenId
        );

        // Transfer funds to lender
        IERC20(stablecoin).transfer(lender, auction.highestBid);
    }
}
```

## NFT Yield Opportunities

### NFT Staking
```solidity
contract NFTStaking {
    mapping(address => uint256[]) public stakedNFTs;
    mapping(address => uint256) public rewardDebt;
    uint256 public rewardPerNFTPerDay = 1e18; // 1 token

    function stakeNFT(address nftAddress, uint256 tokenId) external {
        IERC721(nftAddress).transferFrom(msg.sender, address(this), tokenId);
        stakedNFTs[msg.sender].push(tokenId);
    }

    function claimRewards() external {
        uint256 stakedCount = stakedNFTs[msg.sender].length;
        uint256 daysStaked = (block.timestamp - lastClaimed[msg.sender]) / 1 days;
        uint256 rewards = stakedCount * rewardPerNFTPerDay * daysStaked;

        rewardToken.transfer(msg.sender, rewards);
        lastClaimed[msg.sender] = block.timestamp;
    }
}
```

## NFT Trading Finance

### Conditional Transfers
```solidity
interface INFTTradeCallback {
    function onNFTReceived(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external returns (bytes4);
}

contract NFTEscrow is INFTTradeCallback {
    mapping(uint256 => Trade) public trades;

    struct Trade {
        address seller;
        address buyer;
        address nft;
        uint256 tokenId;
        uint256 price;
        TradeStatus status;
    }

    enum TradeStatus { PENDING, COMPLETED, CANCELLED }

    function initiateTrade(
        address nft,
        uint256 tokenId,
        address buyer,
        uint256 price
    ) external {
        // Buyer deposits price in escrow
        stablecoin.transferFrom(buyer, address(this), price);

        trades[tradeId] = Trade({
            seller: msg.sender,
            buyer: buyer,
            nft: nft,
            tokenId: tokenId,
            price: price,
            status: TradeStatus.PENDING
        });
    }

    function completeTrade(uint256 tradeId) external {
        Trade storage trade = trades[tradeId];
        require(msg.sender == trade.seller || msg.sender == trade.buyer);

        // Transfer NFT to buyer
        IERC721(trade.nft).safeTransferFrom(
            trade.seller,
            trade.buyer,
            trade.tokenId
        );

        // Transfer funds to seller
        stablecoin.transfer(trade.seller, trade.price);

        trade.status = TradeStatus.COMPLETED;
    }
}
```

## Fractional Ownership

### ERC1155 Fractional NFT
```solidity
contract FractionalNFT is ERC1155 {
    struct Fractionalization {
        address originalNFT;
        uint256 originalTokenId;
        uint256 fractionId;
        uint256 totalFractions;
        uint256 owner;
    }

    mapping(uint256 => Fractionalization) public fractions;

    function fractionalize(
        address nftAddress,
        uint256 tokenId,
        uint256 fragmentCount
    ) external returns (uint256) {
        // Transfer original NFT
        IERC721(nftAddress).transferFrom(msg.sender, address(this), tokenId);

        uint256 fractionId = nextFractionId++;

        fractions[fractionId] = Fractionalization({
            originalNFT: nftAddress,
            originalTokenId: tokenId,
            fractionId: fractionId,
            totalFractions: fragmentCount,
            owner: msg.sender
        });

        // Mint fraction tokens
        _mint(msg.sender, fractionId, fragmentCount, "");

        return fractionId;
    }

    function redeem(uint256 fractionId) external {
        Fractionalization storage frac = fractions[fractionId];
        require(balanceOf(msg.sender, fractionId) == frac.totalFractions);

        // Burn all fractions
        _burn(msg.sender, fractionId, frac.totalFractions);

        // Transfer original NFT
        IERC721(frac.originalNFT).safeTransferFrom(
            address(this),
            msg.sender,
            frac.originalTokenId
        );
    }
}
```

## Risk Considerations

### NFT-Specific Risks
```
1. Price Volatility: NFT prices highly volatile
2. Liquidity: NFTs not liquid like fungible tokens
3. Valuation: Difficult to price accurately
4. Counterparty: Borrower may not repay
5. Smart Contract: NFT standard variations
```

### Mitigation
```
1. Conservative LTV: 30-50% for rare NFTs
2. Diversification: Spread across multiple NFTs
3. Oracle Data: Use multiple valuation sources
4. Insurance: Consider NFT insurance
5. Liquidation: Have clear auction mechanisms
```

## Best Practices

- Use ERC721 standard interface
- Implement safeTransferFrom
- Verify NFT authenticity
- Set realistic collateral values
- Monitor liquidation health
- Maintain diversified portfolio
- Keep emergency procedures ready

---

**Key Takeaways**:
- NFTs can serve as collateral
- Fractional ownership enables shared investment
- Auction mechanisms for liquidation
- Higher risk than token-based lending
- Conservative LTV ratios essential
