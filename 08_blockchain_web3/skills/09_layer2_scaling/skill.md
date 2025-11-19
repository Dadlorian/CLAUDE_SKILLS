# Layer 2 Scaling Solutions

## Overview
Build and deploy applications on Layer 2 scaling solutions including rollups, sidechains, and state channels. Master cross-chain communication, L2-specific patterns, and scaling architectures.

## L2 Types

### 1. Optimistic Rollups
- **Optimism**: OP Stack, EVM-equivalent
- **Arbitrum**: Nitro, EVM-compatible
- **Base**: Coinbase L2, built on OP Stack
- **Blast**: Native yield L2
- **Metis**: Decentralized sequencer

**Key Features:**
- 7-day challenge period
- Fraud proof system
- EVM compatibility
- Lower transaction costs
- Higher throughput

### 2. Zero-Knowledge Rollups
- **zkSync Era**: zkEVM, native account abstraction
- **Polygon zkEVM**: EVM-equivalent validity proofs
- **Starknet**: Cairo language, STARKs
- **Scroll**: zkEVM rollup
- **Linea**: ConsenSys zkEVM

**Key Features:**
- Instant finality (after proof)
- Math-based security
- Privacy potential
- Higher computation costs
- Complex development

### 3. Sidechains
- **Polygon PoS**: Independent chain, Ethereum bridge
- **Gnosis Chain**: xDai, stable transactions
- **Skale**: Elastic sidechains
- **Celo**: Mobile-first blockchain

**Key Features:**
- Independent consensus
- Custom gas tokens
- Faster finality
- Trade-off on security
- Bridge dependency

### 4. State Channels
- **Lightning Network**: Bitcoin payments
- **Raiden Network**: Ethereum payments
- **Connext**: Cross-chain channels

**Key Features:**
- Instant finality
- Minimal on-chain footprint
- Best for repeated interactions
- Liquidity requirements

## Optimism Development

### 1. Contract Deployment
```javascript
// hardhat.config.js
module.exports = {
    networks: {
        optimism: {
            url: "https://mainnet.optimism.io",
            accounts: [PRIVATE_KEY],
            chainId: 10
        },
        optimismGoerli: {
            url: "https://goerli.optimism.io",
            accounts: [PRIVATE_KEY],
            chainId: 420
        }
    }
};
```

### 2. Cross-Domain Messaging
```solidity
import { ICrossDomainMessenger } from "@eth-optimism/contracts/libraries/bridge/ICrossDomainMessenger.sol";

contract L1Contract {
    address public l2Contract;
    ICrossDomainMessenger public messenger;

    constructor(address _messenger, address _l2Contract) {
        messenger = ICrossDomainMessenger(_messenger);
        l2Contract = _l2Contract;
    }

    function sendMessageToL2(uint256 value) external {
        bytes memory message = abi.encodeWithSignature(
            "receiveFromL1(uint256)",
            value
        );

        messenger.sendMessage(
            l2Contract,
            message,
            1000000 // gas limit
        );
    }
}

contract L2Contract {
    address public l1Contract;
    ICrossDomainMessenger public messenger;

    event ReceivedFromL1(uint256 value);

    modifier onlyL1Contract() {
        require(
            msg.sender == address(messenger) &&
            messenger.xDomainMessageSender() == l1Contract,
            "Only L1 contract"
        );
        _;
    }

    function receiveFromL1(uint256 value) external onlyL1Contract {
        emit ReceivedFromL1(value);
        // Process message
    }
}
```

### 3. Token Bridging
```solidity
import "@eth-optimism/contracts/L1/messaging/IL1StandardBridge.sol";

contract TokenBridge {
    IL1StandardBridge public bridge;

    function bridgeToken(
        address l1Token,
        address l2Token,
        uint256 amount,
        uint32 l2Gas
    ) external {
        IERC20(l1Token).approve(address(bridge), amount);

        bridge.depositERC20(
            l1Token,
            l2Token,
            amount,
            l2Gas,
            ""
        );
    }

    function bridgeETH(uint32 l2Gas) external payable {
        bridge.depositETH{value: msg.value}(l2Gas, "");
    }
}
```

## Arbitrum Development

### 1. Retryable Tickets
```solidity
import "@arbitrum/nitro-contracts/src/bridge/IInbox.sol";

contract ArbitrumL1Contract {
    IInbox public inbox;

    function sendToL2(
        address l2Contract,
        uint256 value,
        bytes memory data
    ) external payable returns (uint256) {
        uint256 ticketID = inbox.createRetryableTicket{value: msg.value}(
            l2Contract,              // destination
            value,                   // L2 call value
            0,                       // max submission cost
            msg.sender,              // refund address
            msg.sender,              // beneficiary
            1000000,                 // gas limit
            0,                       // max fee per gas
            data                     // calldata
        );

        return ticketID;
    }
}
```

### 2. Arbitrum Specific Features
```solidity
// ArbOS precompiles
import "@arbitrum/nitro-contracts/src/precompiles/ArbSys.sol";

contract ArbitrumContract {
    ArbSys constant arbSys = ArbSys(address(100));

    function getL1BlockNumber() public view returns (uint256) {
        return arbSys.arbBlockNumber();
    }

    function sendToL1(address destination, bytes memory data)
        external
        payable
        returns (uint256)
    {
        return arbSys.sendTxToL1{value: msg.value}(destination, data);
    }
}
```

## zkSync Development

### 1. Contract Deployment
```javascript
import { Wallet, Provider, Contract } from "zksync-web3";
import { Deployer } from "@matterlabs/hardhat-zksync-deploy";

async function deployContract() {
    const provider = new Provider("https://mainnet.era.zksync.io");
    const wallet = new Wallet(PRIVATE_KEY, provider);

    const deployer = new Deployer(hre, wallet);
    const artifact = await deployer.loadArtifact("MyContract");

    const contract = await deployer.deploy(artifact, []);
    await contract.deployed();

    console.log(`Contract deployed to ${contract.address}`);
}
```

### 2. Paymaster Pattern
```solidity
// Allow users to pay fees with ERC20 tokens
contract MyPaymaster is IPaymaster {
    function validateAndPayForPaymasterTransaction(
        bytes32,
        bytes32,
        Transaction calldata _transaction
    ) external payable returns (bytes4 magic, bytes memory context) {
        // Validate transaction
        magic = PAYMASTER_VALIDATION_SUCCESS_MAGIC;

        // Pay for transaction
        uint256 requiredETH = _transaction.gasLimit * _transaction.maxFeePerGas;
        (bool success, ) = payable(BOOTLOADER_FORMAL_ADDRESS).call{
            value: requiredETH
        }("");
        require(success, "Payment failed");

        return (magic, "");
    }

    function postTransaction(
        bytes calldata _context,
        Transaction calldata _transaction,
        bytes32,
        bytes32,
        ExecutionResult _txResult,
        uint256 _maxRefundedGas
    ) external payable override {
        // Refund logic
    }
}
```

### 3. Account Abstraction
```solidity
contract SmartAccount is IAccount {
    function validateTransaction(
        bytes32,
        bytes32 _suggestedSignedHash,
        Transaction calldata _transaction
    ) external payable override returns (bytes4 magic) {
        // Custom validation logic
        magic = ACCOUNT_VALIDATION_SUCCESS_MAGIC;

        // Pay for transaction
        _payForTransaction(_transaction);
    }

    function executeTransaction(
        bytes32,
        bytes32,
        Transaction calldata _transaction
    ) external payable override {
        // Execute the transaction
        _execute(_transaction);
    }

    function _execute(Transaction calldata _transaction) internal {
        address to = address(uint160(_transaction.to));
        uint128 value = Utils.safeCastToU128(_transaction.value);
        bytes memory data = _transaction.data;

        bool success;
        if (to == address(DEPLOYER_SYSTEM_CONTRACT)) {
            success = _executeDeployment(_transaction);
        } else {
            assembly {
                success := call(
                    gas(),
                    to,
                    value,
                    add(data, 0x20),
                    mload(data),
                    0,
                    0
                )
            }
        }

        require(success, "Execution failed");
    }
}
```

## Starknet Development

### 1. Cairo Contract
```cairo
#[starknet::contract]
mod SimpleStorage {
    use starknet::ContractAddress;
    use starknet::get_caller_address;

    #[storage]
    struct Storage {
        stored_data: u128,
        owner: ContractAddress
    }

    #[constructor]
    fn constructor(ref self: ContractState, initial_value: u128) {
        self.stored_data.write(initial_value);
        self.owner.write(get_caller_address());
    }

    #[external(v0)]
    fn set(ref self: ContractState, new_value: u128) {
        assert(get_caller_address() == self.owner.read(), 'Only owner');
        self.stored_data.write(new_value);
    }

    #[external(v0)]
    fn get(self: @ContractState) -> u128 {
        self.stored_data.read()
    }
}
```

### 2. L1-L2 Messaging
```cairo
#[starknet::contract]
mod L2Contract {
    use starknet::ContractAddress;

    #[l1_handler]
    fn handle_l1_message(
        ref self: ContractState,
        from_address: felt252,
        value: u256
    ) {
        // Handle message from L1
        // from_address is the L1 contract address
    }

    fn send_to_l1(
        ref self: ContractState,
        to_address: felt252,
        payload: Span<felt252>
    ) {
        starknet::send_message_to_l1_syscall(
            to_address,
            payload
        );
    }
}
```

## Gas Optimization for L2s

### 1. Calldata Optimization
```solidity
// Minimize calldata by packing data
function optimizedMint(uint256 packed) external {
    // Pack multiple values into single uint256
    uint128 tokenId = uint128(packed >> 128);
    uint128 amount = uint128(packed);

    _mint(msg.sender, tokenId, amount);
}

// Use bytes instead of individual parameters
function batchOperation(bytes calldata data) external {
    // Decode packed data on-chain
    for (uint256 i = 0; i < data.length; i += 32) {
        uint256 value = uint256(bytes32(data[i:i+32]));
        // Process value
    }
}
```

### 2. Storage Patterns
```solidity
// Use mappings instead of arrays when possible
mapping(uint256 => uint256) public data;

// Pack storage variables
struct PackedData {
    uint128 value1;
    uint128 value2;
    // Fits in single slot
}

// Use events for historical data
event DataStored(uint256 indexed id, uint256 value, uint256 timestamp);

function storeData(uint256 id, uint256 value) external {
    // Don't store historical data
    emit DataStored(id, value, block.timestamp);
}
```

## Cross-L2 Communication

### 1. Via L1
```solidity
contract CrossL2Bridge {
    mapping(uint256 => bytes) public pendingMessages;

    // Step 1: Send message from L2A to L1
    function sendToL1(uint256 messageId, bytes memory data) external {
        // L2A -> L1
        l2Bridge.sendMessageToL1(address(this), data);
    }

    // Step 2: L1 receives and forwards to L2B
    function relayToL2B(uint256 messageId, bytes memory data) external {
        // L1 -> L2B
        l2BridgeL2B.sendMessageToL2(targetContract, data);
    }
}
```

### 2. Direct Bridge Protocols
```solidity
// Use protocols like LayerZero, Axelar, or Wormhole
import "@layerzerolabs/contracts/lzApp/NonblockingLzApp.sol";

contract CrossChainContract is NonblockingLzApp {
    function sendCrossChain(
        uint16 dstChainId,
        bytes memory payload
    ) external payable {
        _lzSend(
            dstChainId,
            payload,
            payable(msg.sender),
            address(0),
            bytes(""),
            msg.value
        );
    }

    function _nonblockingLzReceive(
        uint16 _srcChainId,
        bytes memory _srcAddress,
        uint64 _nonce,
        bytes memory _payload
    ) internal override {
        // Handle received message
    }
}
```

## Monitoring & Analytics

### 1. L2 Event Indexing
```javascript
const provider = new ethers.JsonRpcProvider("https://mainnet.optimism.io");
const contract = new ethers.Contract(address, abi, provider);

// Listen to events
contract.on("Transfer", (from, to, amount, event) => {
    console.log(`Transfer: ${from} -> ${to}, ${amount}`);

    // Index to database
    db.transfers.create({
        from,
        to,
        amount: amount.toString(),
        txHash: event.transactionHash,
        blockNumber: event.blockNumber
    });
});
```

### 2. Gas Tracking
```javascript
async function estimateL2Gas(tx) {
    const gasEstimate = await contract.estimateGas[tx.method](...tx.args);
    const feeData = await provider.getFeeData();

    const l2GasCost = gasEstimate * feeData.gasPrice;

    return {
        gasLimit: gasEstimate,
        gasPrice: feeData.gasPrice,
        estimatedCost: l2GasCost
    };
}
```

## Testing on L2s

### 1. Local Development
```javascript
// Hardhat config for L2 fork
module.exports = {
    networks: {
        hardhat: {
            forking: {
                url: "https://mainnet.optimism.io",
                blockNumber: 12345678
            }
        }
    }
};
```

### 2. Integration Tests
```javascript
describe("L2 Contract", function() {
    it("Should work on Optimism", async function() {
        const contract = await deploy("MyContract");

        await contract.doSomething();

        // Test L2-specific features
        const blockNumber = await contract.getL1BlockNumber();
        expect(blockNumber).to.be.gt(0);
    });
});
```

## Security Considerations

### 1. Sequencer Centralization
- Monitor sequencer uptime
- Implement fallback mechanisms
- Plan for censorship resistance

### 2. Bridge Security
- Audit bridge contracts thoroughly
- Monitor bridge TVL and health
- Use established bridges
- Implement timelock for large transfers

### 3. L1 Dependencies
- Monitor L1 gas prices
- Plan for L1 congestion
- Implement message retries

## Resources

### Documentation
- Optimism Docs
- Arbitrum Docs
- zkSync Docs
- Starknet Docs
- Polygon Docs

### Tools
- L2BEAT (Analytics)
- Hop Protocol (Cross-L2)
- Orbiter Finance
- Bungee (Bridge aggregator)

### Testnets
- Optimism Goerli
- Arbitrum Goerli
- zkSync Testnet
- Starknet Goerli

## Conclusion

Layer 2 solutions are critical for blockchain scaling. Understanding different L2 types, their trade-offs, and development patterns is essential for building scalable dApps. Focus on gas optimization, cross-layer communication, and security when developing on L2s.
