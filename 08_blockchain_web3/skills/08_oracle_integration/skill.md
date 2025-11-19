# Oracle Integration

## Overview
Integrate external data into smart contracts using oracle networks, price feeds, and off-chain computation. Master Chainlink, custom oracles, and secure data delivery patterns.

## Oracle Types

### 1. Price Oracles
- **Asset Prices**: Cryptocurrency, forex, commodities
- **Market Data**: Volume, market cap, liquidity
- **DeFi Metrics**: TVL, APY, protocol stats
- **NFT Floor Prices**: Collection valuations

### 2. Data Oracles
- **Weather Data**: Temperature, precipitation, disasters
- **Sports Results**: Scores, outcomes, statistics
- **IoT Sensors**: Real-world measurements
- **Identity Verification**: KYC, credentials

### 3. Computation Oracles
- **VRF (Randomness)**: Verifiable random numbers
- **Automation**: Keeper networks, cron jobs
- **Off-Chain Computing**: Complex calculations
- **ML Inference**: AI model outputs

## Chainlink Integration

### 1. Price Feeds
```solidity
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;

    constructor() {
        // ETH/USD on Ethereum mainnet
        priceFeed = AggregatorV3Interface(
            0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
        );
    }

    function getLatestPrice() public view returns (int) {
        (
            /* uint80 roundID */,
            int price,
            /*uint startedAt*/,
            /*uint timeStamp*/,
            /*uint80 answeredInRound*/
        ) = priceFeed.latestRoundData();

        return price;
    }

    function getDecimals() public view returns (uint8) {
        return priceFeed.decimals();
    }

    function getDescription() public view returns (string memory) {
        return priceFeed.description();
    }

    function getPriceWithSafety() public view returns (int, bool) {
        (
            uint80 roundID,
            int price,
            uint startedAt,
            uint updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        // Safety checks
        require(price > 0, "Invalid price");
        require(updatedAt > 0, "Round not complete");
        require(answeredInRound >= roundID, "Stale price");
        require(block.timestamp - updatedAt < 3600, "Price too old");

        return (price, true);
    }
}
```

### 2. Chainlink VRF (Randomness)
```solidity
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";

contract RandomNumberConsumer is VRFConsumerBaseV2 {
    VRFCoordinatorV2Interface COORDINATOR;

    uint64 s_subscriptionId;
    bytes32 keyHash;
    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;

    uint256[] public s_randomWords;
    uint256 public s_requestId;

    event RandomnessRequested(uint256 requestId);
    event RandomnessFulfilled(uint256 requestId, uint256[] randomWords);

    constructor(
        uint64 subscriptionId,
        address vrfCoordinator,
        bytes32 _keyHash
    ) VRFConsumerBaseV2(vrfCoordinator) {
        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        s_subscriptionId = subscriptionId;
        keyHash = _keyHash;
    }

    function requestRandomWords() external returns (uint256 requestId) {
        requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );

        s_requestId = requestId;
        emit RandomnessRequested(requestId);
        return requestId;
    }

    function fulfillRandomWords(
        uint256 requestId,
        uint256[] memory randomWords
    ) internal override {
        s_randomWords = randomWords;
        emit RandomnessFulfilled(requestId, randomWords);
    }

    function getRandomNumber() public view returns (uint256) {
        require(s_randomWords.length > 0, "No random number available");
        return s_randomWords[0];
    }
}
```

### 3. Chainlink Automation (Keepers)
```solidity
import "@chainlink/contracts/src/v0.8/AutomationCompatible.sol";

contract AutomatedContract is AutomationCompatibleInterface {
    uint256 public counter;
    uint256 public immutable interval;
    uint256 public lastTimeStamp;

    constructor(uint256 updateInterval) {
        interval = updateInterval;
        lastTimeStamp = block.timestamp;
        counter = 0;
    }

    function checkUpkeep(bytes calldata /* checkData */)
        external
        view
        override
        returns (bool upkeepNeeded, bytes memory /* performData */)
    {
        upkeepNeeded = (block.timestamp - lastTimeStamp) > interval;
    }

    function performUpkeep(bytes calldata /* performData */) external override {
        if ((block.timestamp - lastTimeStamp) > interval) {
            lastTimeStamp = block.timestamp;
            counter = counter + 1;
            // Perform automated task
        }
    }
}
```

### 4. Chainlink Any API (HTTP Requests)
```solidity
import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";

contract APIConsumer is ChainlinkClient {
    using Chainlink for Chainlink.Request;

    uint256 public data;
    address private oracle;
    bytes32 private jobId;
    uint256 private fee;

    event DataRequested(bytes32 indexed requestId);
    event DataFulfilled(bytes32 indexed requestId, uint256 data);

    constructor() {
        setChainlinkToken(0x514910771AF9Ca656af840dff83E8264EcF986CA);
        oracle = 0x...; // Oracle address
        jobId = "..."; // Job ID
        fee = 0.1 * 10 ** 18; // 0.1 LINK
    }

    function requestData(string memory url) public returns (bytes32 requestId) {
        Chainlink.Request memory request = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfill.selector
        );

        request.add("get", url);
        request.add("path", "result");

        requestId = sendChainlinkRequestTo(oracle, request, fee);
        emit DataRequested(requestId);
        return requestId;
    }

    function fulfill(bytes32 _requestId, uint256 _data)
        public
        recordChainlinkFulfillment(_requestId)
    {
        data = _data;
        emit DataFulfilled(_requestId, _data);
    }
}
```

## Custom Oracle Implementation

### 1. Simple Oracle Contract
```solidity
contract SimpleOracle {
    address public owner;
    mapping(bytes32 => uint256) public data;

    event DataUpdated(bytes32 indexed key, uint256 value, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function updateData(bytes32 key, uint256 value) external onlyOwner {
        data[key] = value;
        emit DataUpdated(key, value, block.timestamp);
    }

    function getData(bytes32 key) external view returns (uint256) {
        require(data[key] > 0, "No data available");
        return data[key];
    }

    function batchUpdate(bytes32[] calldata keys, uint256[] calldata values)
        external
        onlyOwner
    {
        require(keys.length == values.length, "Length mismatch");

        for (uint256 i = 0; i < keys.length; i++) {
            data[keys[i]] = values[i];
            emit DataUpdated(keys[i], values[i], block.timestamp);
        }
    }
}
```

### 2. Multi-Signature Oracle
```solidity
contract MultiSigOracle {
    struct DataPoint {
        uint256 value;
        uint256 confirmations;
        mapping(address => bool) confirmedBy;
    }

    mapping(bytes32 => DataPoint) public pendingData;
    mapping(address => bool) public isOracle;
    address[] public oracles;
    uint256 public requiredConfirmations;

    event DataProposed(bytes32 indexed key, uint256 value, address proposer);
    event DataConfirmed(bytes32 indexed key, address confirmer);
    event DataFinalized(bytes32 indexed key, uint256 value);

    constructor(address[] memory _oracles, uint256 _required) {
        require(_required > 0 && _required <= _oracles.length, "Invalid threshold");

        for (uint256 i = 0; i < _oracles.length; i++) {
            isOracle[_oracles[i]] = true;
            oracles.push(_oracles[i]);
        }

        requiredConfirmations = _required;
    }

    modifier onlyOracle() {
        require(isOracle[msg.sender], "Not an oracle");
        _;
    }

    function proposeData(bytes32 key, uint256 value) external onlyOracle {
        DataPoint storage dp = pendingData[key];
        require(!dp.confirmedBy[msg.sender], "Already confirmed");

        dp.value = value;
        dp.confirmedBy[msg.sender] = true;
        dp.confirmations = 1;

        emit DataProposed(key, value, msg.sender);

        if (dp.confirmations >= requiredConfirmations) {
            _finalizeData(key);
        }
    }

    function confirmData(bytes32 key) external onlyOracle {
        DataPoint storage dp = pendingData[key];
        require(dp.value > 0, "No pending data");
        require(!dp.confirmedBy[msg.sender], "Already confirmed");

        dp.confirmedBy[msg.sender] = true;
        dp.confirmations++;

        emit DataConfirmed(key, msg.sender);

        if (dp.confirmations >= requiredConfirmations) {
            _finalizeData(key);
        }
    }

    function _finalizeData(bytes32 key) internal {
        DataPoint storage dp = pendingData[key];
        uint256 finalValue = dp.value;

        // Clean up
        delete pendingData[key];

        emit DataFinalized(key, finalValue);
    }
}
```

## TWAP (Time-Weighted Average Price)

### 1. Uniswap V2 TWAP
```solidity
contract UniswapTWAP {
    IUniswapV2Pair public pair;

    uint256 public price0CumulativeLast;
    uint256 public price1CumulativeLast;
    uint256 public blockTimestampLast;

    uint256 public price0Average;
    uint256 public price1Average;

    constructor(address _pair) {
        pair = IUniswapV2Pair(_pair);
        price0CumulativeLast = pair.price0CumulativeLast();
        price1CumulativeLast = pair.price1CumulativeLast();
        (, , blockTimestampLast) = pair.getReserves();
    }

    function update() external {
        (
            uint256 price0Cumulative,
            uint256 price1Cumulative,
            uint256 blockTimestamp
        ) = currentCumulativePrices(address(pair));

        uint256 timeElapsed = blockTimestamp - blockTimestampLast;

        require(timeElapsed >= 3600, "Update too soon"); // Min 1 hour

        price0Average = (price0Cumulative - price0CumulativeLast) / timeElapsed;
        price1Average = (price1Cumulative - price1CumulativeLast) / timeElapsed;

        price0CumulativeLast = price0Cumulative;
        price1CumulativeLast = price1Cumulative;
        blockTimestampLast = blockTimestamp;
    }

    function currentCumulativePrices(address _pair)
        internal
        view
        returns (
            uint256 price0Cumulative,
            uint256 price1Cumulative,
            uint256 blockTimestamp
        )
    {
        blockTimestamp = block.timestamp;
        price0Cumulative = IUniswapV2Pair(_pair).price0CumulativeLast();
        price1Cumulative = IUniswapV2Pair(_pair).price1CumulativeLast();

        (
            uint112 reserve0,
            uint112 reserve1,
            uint32 blockTimestampLast
        ) = IUniswapV2Pair(_pair).getReserves();

        if (blockTimestampLast != blockTimestamp) {
            uint256 timeElapsed = blockTimestamp - blockTimestampLast;
            price0Cumulative += uint256(UQ112x112.encode(reserve1).uqdiv(reserve0)) * timeElapsed;
            price1Cumulative += uint256(UQ112x112.encode(reserve0).uqdiv(reserve1)) * timeElapsed;
        }
    }
}
```

## Oracle Security

### 1. Data Validation
```solidity
function validateOracleData(int256 price, uint256 timestamp)
    internal
    view
    returns (bool)
{
    // Check price is positive
    if (price <= 0) return false;

    // Check timestamp is recent (within 1 hour)
    if (block.timestamp - timestamp > 3600) return false;

    // Check price is within reasonable bounds
    if (price > MAX_PRICE || price < MIN_PRICE) return false;

    return true;
}
```

### 2. Circuit Breakers
```solidity
uint256 public lastPrice;
uint256 public constant MAX_PRICE_DEVIATION = 10; // 10%

function getPriceWithCircuitBreaker() public view returns (uint256) {
    uint256 currentPrice = oracle.getLatestPrice();

    if (lastPrice > 0) {
        uint256 deviation = currentPrice > lastPrice
            ? ((currentPrice - lastPrice) * 100) / lastPrice
            : ((lastPrice - currentPrice) * 100) / lastPrice;

        require(deviation <= MAX_PRICE_DEVIATION, "Price deviation too high");
    }

    return currentPrice;
}
```

### 3. Fallback Mechanisms
```solidity
function getPrice() public view returns (uint256) {
    try primaryOracle.getLatestPrice() returns (int256 price) {
        if (price > 0) return uint256(price);
    } catch {
        // Fallback to secondary oracle
        try secondaryOracle.getLatestPrice() returns (int256 price) {
            if (price > 0) return uint256(price);
        } catch {
            // Use last known good price
            return lastKnownGoodPrice;
        }
    }

    revert("All oracles failed");
}
```

## Off-Chain Workers

### 1. Node.js Oracle Service
```javascript
const ethers = require('ethers');

class OracleService {
    constructor(providerUrl, oracleAddress, privateKey) {
        this.provider = new ethers.JsonRpcProvider(providerUrl);
        this.wallet = new ethers.Wallet(privateKey, this.provider);
        this.oracle = new ethers.Contract(oracleAddress, abi, this.wallet);
    }

    async fetchExternalData(source) {
        const response = await fetch(source);
        const data = await response.json();
        return data.price;
    }

    async updateOracle(key, value) {
        const tx = await this.oracle.updateData(key, value);
        await tx.wait();
        console.log(`Updated ${key} to ${value}`);
    }

    async run() {
        setInterval(async () => {
            try {
                const price = await this.fetchExternalData('https://api.example.com/price');
                await this.updateOracle(
                    ethers.id("ETH/USD"),
                    ethers.parseUnits(price.toString(), 8)
                );
            } catch (error) {
                console.error('Oracle update failed:', error);
            }
        }, 60000); // Update every minute
    }
}
```

## Resources

### Documentation
- Chainlink Documentation
- Band Protocol Docs
- UMA Protocol Docs
- API3 Documentation

### Tools
- Chainlink Price Feeds
- The Graph
- Covalent API
- Moralis API

## Conclusion

Oracle integration is critical for connecting smart contracts to real-world data. Focus on security, reliability, and decentralization when designing oracle systems for production applications.
