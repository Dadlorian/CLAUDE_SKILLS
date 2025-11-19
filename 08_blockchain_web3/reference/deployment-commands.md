# Deployment Commands Reference

## Foundry Deployment

### Basic Deployment
```bash
forge create Contract \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --constructor-args "arg1" "arg2"
```

### With Verification
```bash
forge create Contract \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --etherscan-api-key $ETHERSCAN_KEY \
  --verify
```

### Deploy Script
```bash
forge script script/Deploy.s.sol:DeployScript \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --broadcast \
  --verify
```

## Hardhat Deployment

```bash
npx hardhat run scripts/deploy.ts --network mainnet
npx hardhat verify --network mainnet CONTRACT_ADDRESS "arg1" "arg2"
```

## Verification Only

```bash
# Foundry
forge verify-contract \
  --chain-id 1 \
  --constructor-args $(cast abi-encode "constructor(string,string)" "Name" "Symbol") \
  CONTRACT_ADDRESS \
  src/Contract.sol:Contract \
  $ETHERSCAN_KEY

# Hardhat
npx hardhat verify --network mainnet CONTRACT_ADDRESS "arg1" "arg2"
```

## Multi-Chain Deployment

```bash
# Ethereum
forge create --rpc-url $MAINNET_RPC --private-key $PK Contract

# Polygon
forge create --rpc-url $POLYGON_RPC --private-key $PK Contract

# Arbitrum
forge create --rpc-url $ARBITRUM_RPC --private-key $PK Contract

# Optimism
forge create --rpc-url $OPTIMISM_RPC --private-key $PK Contract
```

## Environment Variables

```bash
# .env file
MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
GOERLI_RPC_URL=https://eth-goerli.g.alchemy.com/v2/YOUR_KEY
PRIVATE_KEY=0x...
ETHERSCAN_API_KEY=YOUR_KEY
```

## Cast Utilities

```bash
# Send transaction
cast send CONTRACT "transfer(address,uint256)" $TO $AMOUNT \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY

# Call view function
cast call CONTRACT "balanceOf(address)" $ADDRESS --rpc-url $RPC_URL

# Get contract storage
cast storage CONTRACT SLOT --rpc-url $RPC_URL
```
