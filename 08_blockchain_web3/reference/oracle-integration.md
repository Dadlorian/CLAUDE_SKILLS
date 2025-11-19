# Oracle Integration Guide

## Overview

Blockchain protocols often need real-world price data to execute financial operations. Oracles are trusted data providers that supply on-chain smart contracts with off-chain information. Oracle integration is critical for DeFi protocols handling lending, swaps, liquidations, and any price-dependent logic.

This guide covers designing, implementing, and securing oracle integrations against manipulation, staleness, and failure scenarios. Oracle security is essential to prevent exploits where attackers manipulate prices to extract value from the protocol.

## Core Concepts

### What are Blockchain Oracles?

Oracles are the bridge between blockchain and off-chain data sources. They provide:
- Real-time asset prices (Chainlink, Band Protocol)
- Event-driven information (premium markets, sports scores)
- Computation results (randomness, VRF)

### Oracle Architecture

```
Off-Chain Data Source → Oracle Node → Smart Contract
```

**Components**:
1. **Data Source**: Price feeds, APIs, databases
2. **Oracle Network**: Decentralized nodes aggregating data
3. **On-Chain Contract**: Receives and verifies oracle data
4. **Consumer Contract**: Uses oracle data for business logic

### Oracle Types

#### 1. Centralized Oracles
- **Single trusted entity** provides data
- **Example**: Project's own price feed
- **Pros**: Simple, fast, cheap
- **Cons**: Single point of failure, trust requirement

#### 2. Decentralized Oracle Networks
- **Multiple independent nodes** provide data
- **Aggregation mechanism** (median, weighted average)
- **Example**: Chainlink network
- **Pros**: Trustless, resilient, transparent
- **Cons**: Higher cost, slightly higher latency

#### 3. DEX-Based Oracles (TWAP)
- **Leverage DEX liquidity** for pricing
- **Example**: Uniswap Time Weighted Average Price
- **Pros**: Decentralized, no external dependencies
- **Cons**: Vulnerable to flash loans, requires liquidity

### Price Feed Security Model

**Key Properties**:
- **Freshness**: How recent is the price?
- **Accuracy**: How close to true market price?
- **Decentralization**: How many sources contribute?
- **Liveness**: Can the data be obtained?

## Oracle Solutions & Integration

### 1. Chainlink Price Feeds (Recommended)

**Architecture**: Decentralized network of nodes, on-chain aggregation

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract ChainlinkPriceConsumer {
    // Reference to the price feed contract
    AggregatorV3Interface internal priceFeed;

    /**
     * @notice Initialize price feed for ETH/USD
     * @dev Use correct address for target blockchain
     */
    constructor() {
        // Ethereum mainnet ETH/USD feed
        priceFeed = AggregatorV3Interface(
            0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
        );
    }

    /**
     * @notice Get latest ETH price with comprehensive safety checks
     * @return price The latest price in USD (18 decimals)
     */
    function getLatestPrice() public view returns (uint256) {
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        // ✅ 1. Validate price is positive
        require(price > 0, "Invalid price: negative or zero");

        // ✅ 2. Check price is recent (within 1 hour)
        require(
            block.timestamp - updatedAt <= 3600,
            "Stale price: data too old"
        );

        // ✅ 3. Verify round is complete and not partial
        require(
            answeredInRound >= roundId,
            "Round not complete: stale answer"
        );

        // ✅ 4. Verify timestamp consistency
        require(startedAt > 0, "Invalid start time");

        return uint256(price);
    }

    /**
     * @notice Get historical price at specific round
     * @param roundId The specific round to query
     * @return price The price in that round
     */
    function getPriceAtRound(uint80 roundId)
        public
        view
        returns (uint256)
    {
        (uint80 id, int256 price, , uint256 updatedAt, ) = priceFeed.getRoundData(
            roundId
        );

        require(id != 0, "Round not found");
        require(price > 0, "Invalid price");
        require(
            block.timestamp - updatedAt <= 3600,
            "Stale round data"
        );

        return uint256(price);
    }

    /**
     * @notice Get decimals for proper price formatting
     * @return Number of decimal places in price
     */
    function getPriceDecimals() public view returns (uint8) {
        return priceFeed.decimals();
    }
}
```

**Security Considerations**:
- **Freshness Requirement**: Set appropriate staleness threshold (usually 1-24 hours)
- **Price Deviation**: Monitor sudden large swings
- **Answer Rounding**: Chainlink prices may lag actual market briefly
- **Hardware Failure**: Multiple independent oracles improve reliability

**Key Safety Checks** (ESSENTIAL):
1. ✅ `price > 0` - Validate price is positive
2. ✅ `updatedAt >= block.timestamp - maxAge` - Check freshness
3. ✅ `answeredInRound >= roundId` - Verify round completeness
4. ✅ Deviation bounds - Reject suspicious price changes

**Cost**: Chainlink VRF2 + premium feeds ~0.1-1 LINK per update

**Chainlink Feed Addresses**: https://docs.chain.link/data-feeds/price-feeds/addresses

### 2. Uniswap V3 TWAP (Time Weighted Average Price)

**Mechanism**: Calculate average price over time window using Uniswap's historical data

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import "@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol";

contract UniswapV3TWAPOracle {
    // Uniswap V3 pool for ETH/USDC
    address constant POOL = 0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8;

    /**
     * @notice Calculate time-weighted average price over specified period
     * @param secondsAgo How far back to calculate average (e.g., 1800 = 30 min)
     * @return price The TWAP price (scaled by 1e18)
     */
    function getTWAPPrice(uint32 secondsAgo)
        public
        view
        returns (uint256)
    {
        require(secondsAgo > 0, "Invalid time period");
        require(secondsAgo <= 86400, "Max 24 hours"); // Reasonable limit

        IUniswapV3Pool pool = IUniswapV3Pool(POOL);

        // Get tick data for two timestamps: now and secondsAgo
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = secondsAgo;  // Earlier timestamp
        secondsAgos[1] = 0;           // Current timestamp

        (int56[] memory tickCumulatives, ) = pool.observe(secondsAgos);

        // Calculate average tick over period
        int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];
        int24 arithmeticMeanTick = int24(
            tickCumulativesDelta / int56(uint56(secondsAgo))
        );

        // Convert tick to actual price
        uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick(arithmeticMeanTick);

        // Calculate token amount
        uint256 quoteAmount = OracleLibrary.getQuoteAtTick(
            arithmeticMeanTick,
            1e6,  // 1 USDC (6 decimals)
            0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48, // USDC token
            0xC02aaA39b223FE8D0A0e8e4F27ead9083C756Cc2  // WETH token
        );

        return quoteAmount; // Price in wei
    }

    /**
     * @notice Get TWAP with security validations
     * @param timeWindow Time period for average
     * @return price Safe-to-use TWAP price
     */
    function getSafeTWAPPrice(uint32 timeWindow)
        public
        view
        returns (uint256)
    {
        // ✅ 1. Validate time window
        require(timeWindow > 60, "Too short (min 60 seconds)");
        require(timeWindow <= 86400, "Too long (max 24 hours)");

        // ✅ 2. Get TWAP
        uint256 twapPrice = getTWAPPrice(timeWindow);

        // ✅ 3. Validate price is reasonable
        require(twapPrice > 0, "Invalid TWAP");

        // ✅ 4. Optional: Check against previous TWAP
        // Reject if change > 10%
        uint256 previousTWAP = getPreviousTWAPPrice(timeWindow);
        require(
            (twapPrice * 100) / previousTWAP >= 90 &&
            (twapPrice * 100) / previousTWAP <= 110,
            "Excessive price change"
        );

        return twapPrice;
    }

    function getPreviousTWAPPrice(uint32 timeWindow)
        internal
        view
        returns (uint256)
    {
        // Implementation would track TWAP history
        // Simplified here
        return getTWAPPrice(timeWindow);
    }
}
```

**Advantages**:
- Decentralized (leverages Uniswap liquidity)
- No external oracle cost
- Resistant to short-term price manipulation

**Disadvantages**:
- Vulnerable to flash loan attacks on low-liquidity pairs
- Requires adequate liquidity
- Higher gas cost to compute

**Usage Pattern**:
- 15-30 minute TWAP: Good for most operations
- 1 hour TWAP: Better security but higher latency
- Avoid short periods (<1 min) due to flash loan vulnerability

### 3. Band Protocol Integration

```solidity
interface IStdReference {
    function getReferenceData(
        string memory _base,
        string memory _quote
    ) external view returns (ReferenceData memory);

    struct ReferenceData {
        uint64 rate;           // Rate of base/quote
        uint64 lastUpdatedBase;
        uint64 lastUpdatedQuote;
    }
}

contract BandOracleConsumer {
    IStdReference public bandOracle;

    constructor(address _bandOracle) {
        bandOracle = IStdReference(_bandOracle);
    }

    function getETHPrice() public view returns (uint256) {
        IStdReference.ReferenceData memory data = bandOracle.getReferenceData(
            "ETH",
            "USD"
        );

        require(data.rate > 0, "Invalid rate");

        // Check freshness (both base and quote)
        require(
            block.timestamp - uint256(data.lastUpdatedBase) <= 3600,
            "Stale base price"
        );
        require(
            block.timestamp - uint256(data.lastUpdatedQuote) <= 3600,
            "Stale quote price"
        );

        return uint256(data.rate);
    }
}
```

**Characteristics**:
- Multi-source data aggregation
- Cost: ~5-10 BAND per request
- Good for exotic asset pairs
- Decentralized validator set

### 4. API3 (Decentralized APIs)

```solidity
interface IProxy {
    function read() external view returns (bytes memory);
}

contract API3Consumer {
    IProxy public dataFeed;

    constructor(address dataFeedAddress) {
        dataFeed = IProxy(dataFeedAddress);
    }

    function getETHPrice() public view returns (uint256) {
        (uint256 value, uint256 timestamp) = abi.decode(
            dataFeed.read(),
            (uint256, uint256)
        );

        // Validate timestamp
        require(
            block.timestamp - timestamp <= 3600,
            "Stale price"
        );

        return value;
    }
}
```

## Oracle Security Best Practices

### 1. Multiple Oracle Sources

```solidity
contract MultiOraclePrice {
    address chainlinkFeed;
    address uniswapPool;
    address bandOracle;

    function getPrice() public view returns (uint256) {
        uint256 chainlinkPrice = getChainlinkPrice();
        uint256 uniswapPrice = getUniswapPrice();
        uint256 bandPrice = getBandPrice();

        // Use median to prevent single-source manipulation
        uint256[] memory prices = new uint256[](3);
        prices[0] = chainlinkPrice;
        prices[1] = uniswapPrice;
        prices[2] = bandPrice;

        // Sort and return median
        return getMedian(prices);
    }

    function getMedian(uint256[] memory values) internal pure returns (uint256) {
        // Sort array and return middle value
        quickSort(values, 0, values.length - 1);
        return values[values.length / 2];
    }
}
```

### 2. Price Deviation Limits

```solidity
contract PriceDeviationCheck {
    mapping(address => uint256) public lastPrice;
    uint256 constant MAX_PRICE_DEVIATION = 10; // 10%

    function checkPriceDeviation(address token, uint256 currentPrice)
        internal
    {
        uint256 previousPrice = lastPrice[token];

        if (previousPrice == 0) {
            lastPrice[token] = currentPrice;
            return;
        }

        uint256 change = (currentPrice * 100) / previousPrice;

        // Change should be between 90-110 (±10%)
        require(
            change >= 90 && change <= 110,
            "Excessive price deviation"
        );

        lastPrice[token] = currentPrice;
    }
}
```

### 3. Fallback Mechanisms

```solidity
contract OracleWithFallback {
    address primary;
    address fallback1;
    address fallback2;

    function getSafePrice() public view returns (uint256) {
        try this.getPrimaryPrice() returns (uint256 price) {
            return price;
        } catch {
            try this.getFallback1Price() returns (uint256 price) {
                return price;
            } catch {
                return getFallback2Price(); // Last resort
            }
        }
    }
}
```

### 4. Circuit Breakers

```solidity
contract OracleCircuitBreaker {
    uint256 minPrice;
    uint256 maxPrice;
    bool paused;

    function setCircuitBreakerLimits(uint256 min, uint256 max) external onlyAdmin {
        minPrice = min;
        maxPrice = max;
    }

    function getSafePrice() public view returns (uint256) {
        require(!paused, "Circuit breaker activated");

        uint256 price = getOraclePrice();

        require(price >= minPrice && price <= maxPrice, "Price out of bounds");

        return price;
    }

    function activateCircuitBreaker() external onlyAdmin {
        paused = true;
        emit CircuitBreakerActivated();
    }
}
```

## Oracle Security Checklist

**Before Using Oracle Data**:
- [ ] Multiple data sources (at least 2)
- [ ] Staleness checks implemented
- [ ] Price deviation bounds validated
- [ ] Fallback mechanisms ready
- [ ] Circuit breakers configured
- [ ] Flash loan protection enabled (if TWAP)
- [ ] Rate limiting on oracle calls
- [ ] Emergency pause capability

**Oracle Configuration**:
- [ ] Correct contract addresses verified
- [ ] Appropriate staleness threshold set
- [ ] Reasonable price deviation limits
- [ ] Uptime monitoring configured
- [ ] Cost analysis completed

**Monitoring & Response**:
- [ ] Oracle data logged for analysis
- [ ] Anomalies detected and alerted
- [ ] Historical price data stored
- [ ] Incident response plan ready

## Common Oracle Vulnerabilities

| Vulnerability | Example | Mitigation |
|---------------|---------|-----------​|
| Flash Loan Attack | Manipulate TWAP with large trade | Use longer time windows, Chainlink |
| Stale Price | Using outdated oracle data | Check `updatedAt` < max_age |
| Single Oracle | One source fails | Use multiple oracle sources |
| Price Deviation | Sudden 50% change accepted | Set deviation bounds |
| Oracle Downtime | Feed goes offline | Implement fallback mechanisms |

## Production Oracle Architecture

```solidity
contract ProductionOracleConsumer {
    // Primary: Chainlink (most reliable)
    address chainlinkFeed;

    // Fallback 1: Uniswap V3 TWAP (decentralized)
    address uniswapPool;

    // Fallback 2: Band Protocol (multi-source)
    address bandOracle;

    // Configuration
    uint256 constant MAX_PRICE_AGE = 3600; // 1 hour
    uint256 constant MAX_DEVIATION = 5; // 5%
    bool pausedForMaintenance;

    /**
     * @notice Get price with full security checks and fallbacks
     * @return price The current safe price
     */
    function getPrice() external view returns (uint256) {
        require(!pausedForMaintenance, "Oracle paused");

        try this.chainlinkPrice() returns (uint256 price) {
            validatePrice(price);
            return price;
        } catch {
            try this.uniswapPrice() returns (uint256 price) {
                validatePrice(price);
                return price;
            } catch {
                uint256 fallbackPrice = bandPrice();
                validatePrice(fallbackPrice);
                return fallbackPrice;
            }
        }
    }

    function validatePrice(uint256 price) internal view {
        require(price > 0, "Invalid price");
        checkDeviation(price);
    }

    function checkDeviation(uint256 currentPrice) internal view {
        // Implementation
    }
}
```

---

**Remember**: Oracle security is not optional. A single bad oracle integration can drain entire protocols. Always use defense-in-depth with multiple sources and comprehensive validation.
