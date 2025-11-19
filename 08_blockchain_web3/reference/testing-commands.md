# Testing Commands Cheat Sheet

## Foundry Testing

### Basic Tests
```bash
forge test                           # Run all tests
forge test -vv                       # Verbose (show console.log)
forge test -vvvv                     # Max verbosity (traces)
forge test --match-test testName    # Specific test
forge test --match-contract ContractTest  # Specific contract
forge test --gas-report              # Show gas usage
```

### Coverage
```bash
forge coverage                       # Basic coverage
forge coverage --report lcov         # Generate LCOV report
genhtml lcov.info -o coverage        # HTML report
forge coverage --report summary      # Summary only
```

### Fuzzing
```bash
forge test --fuzz-runs 10000        # More fuzz runs
forge test --fuzz-seed 0x1234       # Specific seed
```

### Fork Testing
```bash
forge test --fork-url $MAINNET_RPC
forge test --fork-url $MAINNET_RPC --fork-block-number 18000000
```

### Gas Snapshots
```bash
forge snapshot                       # Create snapshot
forge snapshot --diff .gas-snapshot  # Compare to existing
forge snapshot --check               # CI check (fails if changed)
```

## Hardhat Testing

```bash
npx hardhat test                     # Run all tests
npx hardhat test --grep "should transfer"  # Specific test
npx hardhat test --gas-reporter      # Gas report
npx hardhat coverage                 # Coverage
```

## Test Structure

```solidity
contract MyTest is Test {
    function setUp() public {
        // Setup before each test
    }

    function test_BasicFunctionality() public {
        // Test implementation
    }

    function testFuzz_InputValidation(uint256 amount) public {
        // Fuzz test
    }

    function testFail_RevertCondition() public {
        // Should revert
    }
}
```
