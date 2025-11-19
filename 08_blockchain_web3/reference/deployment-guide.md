# Multi-Chain Deployment Guide

## Ethereum Mainnet
- Gas: High (20-200 gwei)
- Finality: ~15 minutes (25 blocks)
- RPC: Infura, Alchemy, Quicknode

## Polygon
- Gas: Low (30-100 gwei)
- Finality: ~5 minutes
- RPC: https://polygon-rpc.com
- Bridge: Official Polygon bridge

## Arbitrum
- Gas: Low
- Finality: ~1-2 minutes
- L1-L2 Bridge: 10-15 minutes
- RPC: https://arb1.arbitrum.io/rpc

## Optimism
- Gas: Low
- Finality: ~1 minute
- L1-L2 Bridge: ~7 days withdrawal
- RPC: https://mainnet.optimism.io

## Base (Coinbase L2)
- Gas: Low
- Finality: Fast
- EVM equivalent
- RPC: https://mainnet.base.org

## Deployment Checklist
- [ ] Set correct RPC URL
- [ ] Verify constructor parameters
- [ ] Test on testnet first
- [ ] Verify on block explorer
- [ ] Initialize contracts
- [ ] Transfer ownership to multisig
- [ ] Set up monitoring

## Hardhat Multi-Chain Config
```javascript
networks: {
  mainnet: {
    url: process.env.MAINNET_RPC_URL,
    accounts: [process.env.PRIVATE_KEY],
    chainId: 1,
  },
  polygon: {
    url: "https://polygon-rpc.com",
    accounts: [process.env.PRIVATE_KEY],
    chainId: 137,
  },
  arbitrum: {
    url: "https://arb1.arbitrum.io/rpc",
    accounts: [process.env.PRIVATE_KEY],
    chainId: 42161,
  },
}
```
