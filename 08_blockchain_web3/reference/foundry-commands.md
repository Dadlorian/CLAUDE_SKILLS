# Foundry Commands Reference

## Setup
```bash
forge init my-project
forge install OpenZeppelin/openzeppelin-contracts
forge remappings > remappings.txt
```

## Build & Test
```bash
forge build                          # Compile
forge test                           # Run all tests
forge test --match-test test_Name   # Run specific test
forge test -vvvv                     # Max verbosity
forge test --gas-report              # Gas usage report
```

## Coverage & Analysis
```bash
forge coverage                       # Code coverage
forge coverage --report lcov         # LCOV format
forge snapshot                       # Gas snapshots
forge snapshot --diff                # Compare snapshots
```

## Deployment
```bash
forge create Contract --rpc-url $RPC --private-key $PK
forge verify-contract ADDRESS Contract --chain-id 1
```

## Utilities
```bash
cast call ADDRESS "balanceOf(address)" $ADDR  # Call view function
cast send ADDRESS "transfer(address,uint)" $TO $AMT --private-key $PK
cast block-number                    # Current block
cast balance ADDRESS                 # ETH balance
```

## Local Node
```bash
anvil                                # Start local node
anvil --fork-url $MAINNET_RPC       # Fork mainnet
```
