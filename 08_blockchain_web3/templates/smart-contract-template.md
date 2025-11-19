# Smart Contract Development Template

This template guides you through creating production-ready smart contracts with security and gas optimization in mind.

## Project Setup Template

### Directory Structure
```
project-name/
├── contracts/
│   ├── core/              # Core protocol logic
│   ├── interfaces/        # Contract interfaces
│   ├── libraries/         # Reusable libraries
│   ├── mocks/            # Testing mocks
│   └── periphery/        # Helper contracts
├── test/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fork/             # Fork tests
├── scripts/
│   ├── deploy.ts         # Deployment scripts
│   └── verify.ts         # Verification scripts
├── foundry.toml          # Foundry config
├── hardhat.config.ts     # Hardhat config
└── .env.example
```

## Foundry Configuration

```toml
# foundry.toml
[profile.default]
src = "contracts"
out = "out"
libs = ["lib"]
solc = "0.8.23"
optimizer = true
optimizer_runs = 200
via_ir = false

[profile.ci]
fuzz = { runs = 10000 }
invariant = { runs = 1000 }

[fmt]
line_length = 100
tab_width = 4
bracket_spacing = true
```

## Hardhat Configuration

```typescript
// hardhat.config.ts
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@openzeppelin/hardhat-upgrades";
import "hardhat-gas-reporter";
import "solidity-coverage";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.23",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: false,
    },
  },
  networks: {
    hardhat: {
      forking: {
        url: process.env.MAINNET_RPC_URL || "",
        enabled: process.env.FORK === "true",
      },
    },
    goerli: {
      url: process.env.GOERLI_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
    mainnet: {
      url: process.env.MAINNET_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_API_KEY,
  },
};

export default config;
```

## ERC-20 Token Template

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title MyToken
 * @notice Production-ready ERC-20 token with advanced features
 * @dev Includes:
 * - Burnable tokens
 * - EIP-2612 Permit (gasless approvals)
 * - Role-based access control
 * - Emergency pause mechanism
 * - Capped supply
 */
contract MyToken is ERC20, ERC20Burnable, ERC20Permit, AccessControl, Pausable {
    /// @notice Role for minting new tokens
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    /// @notice Role for pausing/unpausing
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice Maximum supply cap
    uint256 public immutable cap;

    /// @dev Emitted when tokens are minted
    event TokensMinted(address indexed to, uint256 amount);

    /// @dev Custom errors for gas efficiency
    error ExceedsCap(uint256 amount, uint256 cap);
    error ZeroAddress();
    error ZeroAmount();

    /**
     * @notice Initializes the token
     * @param name Token name
     * @param symbol Token symbol
     * @param initialSupply Initial token supply
     * @param maxCap Maximum token supply
     */
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        uint256 maxCap
    ) ERC20(name, symbol) ERC20Permit(name) {
        if (maxCap == 0) revert ZeroAmount();
        if (initialSupply > maxCap) revert ExceedsCap(initialSupply, maxCap);

        cap = maxCap;

        // Grant roles to deployer
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);

        // Mint initial supply
        if (initialSupply > 0) {
            _mint(msg.sender, initialSupply);
        }
    }

    /**
     * @notice Mints new tokens
     * @param to Recipient address
     * @param amount Amount to mint
     */
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) whenNotPaused {
        if (to == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (totalSupply() + amount > cap) revert ExceedsCap(totalSupply() + amount, cap);

        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @notice Pauses all token transfers
     * @dev Can only be called by PAUSER_ROLE
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @notice Unpauses token transfers
     * @dev Can only be called by PAUSER_ROLE
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Hook that is called before any transfer of tokens
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
}
```

## Test Template (Foundry)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "forge-std/Test.sol";
import "../contracts/MyToken.sol";

contract MyTokenTest is Test {
    MyToken public token;

    address public owner;
    address public minter;
    address public user1;
    address public user2;

    uint256 constant INITIAL_SUPPLY = 1_000_000e18;
    uint256 constant MAX_CAP = 10_000_000e18;

    event TokensMinted(address indexed to, uint256 amount);

    function setUp() public {
        owner = address(this);
        minter = makeAddr("minter");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");

        token = new MyToken("My Token", "MTK", INITIAL_SUPPLY, MAX_CAP);
        token.grantRole(token.MINTER_ROLE(), minter);
    }

    /*//////////////////////////////////////////////////////////////
                           DEPLOYMENT TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Deployment() public {
        assertEq(token.name(), "My Token");
        assertEq(token.symbol(), "MTK");
        assertEq(token.totalSupply(), INITIAL_SUPPLY);
        assertEq(token.cap(), MAX_CAP);
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY);
    }

    function test_InitialRoles() public {
        assertTrue(token.hasRole(token.DEFAULT_ADMIN_ROLE(), owner));
        assertTrue(token.hasRole(token.MINTER_ROLE(), owner));
        assertTrue(token.hasRole(token.PAUSER_ROLE(), owner));
        assertTrue(token.hasRole(token.MINTER_ROLE(), minter));
    }

    /*//////////////////////////////////////////////////////////////
                            MINTING TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Mint() public {
        uint256 amount = 1000e18;

        vm.prank(minter);
        vm.expectEmit(true, false, false, true);
        emit TokensMinted(user1, amount);
        token.mint(user1, amount);

        assertEq(token.balanceOf(user1), amount);
        assertEq(token.totalSupply(), INITIAL_SUPPLY + amount);
    }

    function testFuzz_Mint(address to, uint96 amount) public {
        vm.assume(to != address(0));
        vm.assume(amount > 0);
        vm.assume(INITIAL_SUPPLY + amount <= MAX_CAP);

        vm.prank(minter);
        token.mint(to, amount);

        assertEq(token.balanceOf(to), amount);
    }

    function test_RevertWhen_MintExceedsCap() public {
        uint256 exceedingAmount = MAX_CAP - INITIAL_SUPPLY + 1;

        vm.prank(minter);
        vm.expectRevert(
            abi.encodeWithSelector(
                MyToken.ExceedsCap.selector,
                INITIAL_SUPPLY + exceedingAmount,
                MAX_CAP
            )
        );
        token.mint(user1, exceedingAmount);
    }

    function test_RevertWhen_MintToZeroAddress() public {
        vm.prank(minter);
        vm.expectRevert(MyToken.ZeroAddress.selector);
        token.mint(address(0), 1000e18);
    }

    function test_RevertWhen_MintByNonMinter() public {
        vm.prank(user1);
        vm.expectRevert();
        token.mint(user1, 1000e18);
    }

    /*//////////////////////////////////////////////////////////////
                           TRANSFER TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Transfer() public {
        uint256 amount = 100e18;

        vm.prank(owner);
        token.transfer(user1, amount);

        assertEq(token.balanceOf(user1), amount);
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY - amount);
    }

    function test_RevertWhen_TransferWhilePaused() public {
        token.pause();

        vm.prank(owner);
        vm.expectRevert("Pausable: paused");
        token.transfer(user1, 100e18);
    }

    /*//////////////////////////////////////////////////////////////
                            BURNING TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Burn() public {
        uint256 burnAmount = 100e18;
        uint256 initialBalance = token.balanceOf(owner);

        token.burn(burnAmount);

        assertEq(token.balanceOf(owner), initialBalance - burnAmount);
        assertEq(token.totalSupply(), INITIAL_SUPPLY - burnAmount);
    }

    /*//////////////////////////////////////////////////////////////
                            PERMIT TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Permit() public {
        uint256 privateKey = 0xA11CE;
        address alice = vm.addr(privateKey);

        // Mint some tokens to alice
        vm.prank(minter);
        token.mint(alice, 1000e18);

        uint256 amount = 500e18;
        uint256 deadline = block.timestamp + 1 hours;

        // Create permit signature
        bytes32 permitHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                alice,
                user1,
                amount,
                token.nonces(alice),
                deadline
            )
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", token.DOMAIN_SEPARATOR(), permitHash)
        );

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

        // Execute permit
        token.permit(alice, user1, amount, deadline, v, r, s);

        assertEq(token.allowance(alice, user1), amount);
    }

    /*//////////////////////////////////////////////////////////////
                            PAUSE TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Pause() public {
        assertFalse(token.paused());

        token.pause();
        assertTrue(token.paused());

        token.unpause();
        assertFalse(token.paused());
    }

    function test_RevertWhen_PauseByNonPauser() public {
        vm.prank(user1);
        vm.expectRevert();
        token.pause();
    }

    /*//////////////////////////////////////////////////////////////
                         GAS BENCHMARKS
    //////////////////////////////////////////////////////////////*/

    function testGas_Transfer() public {
        token.transfer(user1, 100e18);
    }

    function testGas_Mint() public {
        vm.prank(minter);
        token.mint(user1, 100e18);
    }
}
```

## Deployment Script Template

```typescript
// scripts/deploy.ts
import { ethers } from "hardhat";
import { MyToken } from "../typechain-types";

async function main() {
  console.log("Starting deployment...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deployment parameters
  const TOKEN_NAME = "My Token";
  const TOKEN_SYMBOL = "MTK";
  const INITIAL_SUPPLY = ethers.utils.parseEther("1000000"); // 1M tokens
  const MAX_CAP = ethers.utils.parseEther("10000000"); // 10M tokens

  // Deploy token
  const MyToken = await ethers.getContractFactory("MyToken");
  const token = await MyToken.deploy(
    TOKEN_NAME,
    TOKEN_SYMBOL,
    INITIAL_SUPPLY,
    MAX_CAP
  ) as MyToken;

  await token.deployed();
  console.log("Token deployed to:", token.address);

  // Wait for confirmations
  console.log("Waiting for block confirmations...");
  await token.deployTransaction.wait(6);

  // Verify on Etherscan
  if (network.name !== "hardhat" && network.name !== "localhost") {
    console.log("Verifying contract on Etherscan...");
    try {
      await hre.run("verify:verify", {
        address: token.address,
        constructorArguments: [
          TOKEN_NAME,
          TOKEN_SYMBOL,
          INITIAL_SUPPLY,
          MAX_CAP,
        ],
      });
      console.log("Contract verified!");
    } catch (error) {
      console.log("Verification failed:", error);
    }
  }

  // Save deployment info
  const deployment = {
    network: network.name,
    token: token.address,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    parameters: {
      name: TOKEN_NAME,
      symbol: TOKEN_SYMBOL,
      initialSupply: INITIAL_SUPPLY.toString(),
      maxCap: MAX_CAP.toString(),
    },
  };

  console.log("Deployment complete:", deployment);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

## Security Checklist

Before deploying, verify:

- [ ] All functions have appropriate access control
- [ ] Custom errors used for gas efficiency
- [ ] No re-entrancy vulnerabilities
- [ ] Overflow/underflow protection (Solidity 0.8+)
- [ ] External calls checked for return values
- [ ] Emergency pause mechanism implemented
- [ ] Events emitted for all state changes
- [ ] NatSpec documentation complete
- [ ] Comprehensive test coverage (>95%)
- [ ] Gas optimization reviewed
- [ ] Upgradability strategy documented
- [ ] Deployment script tested on testnet
- [ ] Etherscan verification prepared
- [ ] Multi-sig for admin operations
- [ ] Monitoring and alerts configured

## Gas Optimization Tips

1. **Use custom errors** instead of require strings (Solidity 0.8.4+)
2. **Pack storage variables** into 32-byte slots
3. **Use immutable** for constructor-set constants
4. **Use calldata** for read-only function parameters
5. **Cache storage reads** in local variables
6. **Use unchecked** blocks for safe arithmetic
7. **Avoid unnecessary storage writes**
8. **Batch operations** when possible
9. **Use events** instead of storing data when appropriate
10. **Optimize loops** and avoid unbounded iterations

## Additional Resources

- OpenZeppelin Contracts: https://docs.openzeppelin.com/contracts
- Solidity Documentation: https://docs.soliditylang.org
- Foundry Book: https://book.getfoundry.sh
- Ethereum Security Best Practices: https://consensys.github.io/smart-contract-best-practices
