# ERC Standards Comparison

## Token Standards

| Standard | Type | Use Case | Transferable | Fungible |
|----------|------|----------|--------------|----------|
| ERC-20 | Token | Currencies, governance | ✅ | ✅ |
| ERC-721 | NFT | Unique collectibles | ✅ | ❌ |
| ERC-1155 | Multi | Gaming, semi-fungible | ✅ | Both |
| ERC-5192 | Soulbound | Credentials, identity | ❌ | ❌ |

## Advanced Features

| Standard | Purpose | Key Feature |
|----------|---------|-------------|
| ERC-2612 | Permit | Gasless approvals via signature |
| ERC-4626 | Vaults | Tokenized yield-bearing vaults |
| ERC-2981 | Royalties | NFT creator royalties |
| ERC-4907 | Rental | Separate owner and user rights |
| ERC-5805 | Voting | Governance and delegation |
| ERC-2535 | Diamond | Modular upgradeable contracts |

## When to Use

**ERC-20**: Standard tokens (USDC, DAI, UNI)
**ERC-721**: Unique art, real estate, domain names
**ERC-1155**: Gaming items, tickets, memberships
**ERC-2612**: Enable gasless trading
**ERC-4626**: Yield vaults, strategies
**ERC-2981**: NFT marketplaces with royalties
**ERC-4907**: NFT rentals, subscriptions
**ERC-5192**: Non-transferable badges, certifications

## Implementation Complexity

| Standard | Complexity | OpenZeppelin |
|----------|-----------|--------------|
| ERC-20 | ⭐ Low | ✅ |
| ERC-721 | ⭐⭐ Medium | ✅ |
| ERC-1155 | ⭐⭐⭐ Medium | ✅ |
| ERC-2612 | ⭐⭐ Medium | ✅ (ERC20Permit) |
| ERC-4626 | ⭐⭐⭐ Medium | ✅ |
| ERC-2981 | ⭐ Low | ✅ (ERC2981) |
| ERC-2535 | ⭐⭐⭐⭐⭐ Very High | ❌ |
