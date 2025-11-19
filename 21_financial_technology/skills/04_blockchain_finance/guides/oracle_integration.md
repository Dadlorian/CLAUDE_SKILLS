# Oracle Integration Guide

## Chainlink Price Feeds

### Basic Integration
```solidity
pragma solidity ^0.8.9;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceFeedExample {
    AggregatorV3Interface public priceFeed;

    constructor(address priceFeedAddress) {
        priceFeed = AggregatorV3Interface(priceFeedAddress);
    }

    function getLatestPrice() public view returns (uint256) {
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        // Check if price is stale
        require(block.timestamp - updatedAt < 1 hours, "Price stale");

        // Convert to uint256 and adjust decimals
        return uint256(price) * 1e10; // Convert 8 decimals to 18
    }

    function getPriceWithDecimals() public view returns (uint256, uint8) {
        int256 price = priceFeed.latestAnswer();
        uint8 decimals = priceFeed.decimals();

        return (uint256(price), decimals);
    }
}
```

### Price Data Structure
```solidity
contract OracleConsumer {
    AggregatorV3Interface public ethUsdFeed;
    AggregatorV3Interface public usdcUsdFeed;

    constructor(
        address ethFeed,
        address usdcFeed
    ) {
        ethUsdFeed = AggregatorV3Interface(ethFeed);
        usdcUsdFeed = AggregatorV3Interface(usdcFeed);
    }

    // Get ETH price
    function getETHPrice() public view returns (uint256) {
        (,int256 price,,,) = ethUsdFeed.latestRoundData();
        return uint256(price) * 1e10;
    }

    // Get USDC price
    function getUSDCPrice() public view returns (uint256) {
        (,int256 price,,,) = usdcUsdFeed.latestRoundData();
        return uint256(price) * 1e10;
    }

    // Calculate derived price
    function calculatePrice(
        uint256 ethAmount
    ) public view returns (uint256) {
        uint256 ethPrice = getETHPrice();
        return (ethAmount * ethPrice) / 1e18;
    }
}
```

### Staleness Checks
```solidity
contract RobustOracle {
    uint256 constant STALENESS_THRESHOLD = 1 hours;

    function getSafePrice(AggregatorV3Interface feed) public view returns (uint256) {
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = feed.latestRoundData();

        // Check for zero price
        require(price > 0, "Invalid price");

        // Check staleness
        require(
            block.timestamp - updatedAt < STALENESS_THRESHOLD,
            "Price too stale"
        );

        // Check if answering completed
        require(answeredInRound >= roundId, "Incomplete answer");

        return uint256(price);
    }
}
```

## Uniswap TWAP (Time-Weighted Average Price)

### TWAP Implementation
```solidity
pragma solidity ^0.8.9;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import "@uniswap/v3-core/contracts/libraries/TickMath.sol";

contract UniswapTWAP {
    IUniswapV3Pool public pool;
    address public token0;
    address public token1;

    constructor(address _pool) {
        pool = IUniswapV3Pool(_pool);
        token0 = pool.token0();
        token1 = pool.token1();
    }

    function getTWAP(uint32 timeWindow) public view returns (uint256) {
        // Get time-weighted average tick
        (int24 tick, ) = getTwapTick(timeWindow);

        // Convert tick to price
        uint160 sqrtPrice = TickMath.getSqrtRatioAtTick(tick);

        // Convert sqrt price to price
        uint256 price = (uint256(sqrtPrice) ** 2 * 1e18) >> 192;

        return price;
    }

    function getTwapTick(uint32 timeWindow) internal view returns (int24, bool) {
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = timeWindow;
        secondsAgos[1] = 0;

        (int56[] memory tickCumulatives,) = pool.observe(secondsAgos);

        int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];

        int24 tick = int24(tickCumulativesDelta / int56(uint56(timeWindow)));

        if (tickCumulativesDelta < 0 && (tickCumulativesDelta % int56(uint56(timeWindow)) != 0))
            tick--;

        return (tick, true);
    }
}
```

## Multiple Oracle Aggregation

### Median Price
```solidity
contract OracleAggregator {
    AggregatorV3Interface[] public oracles;

    constructor(address[] memory _oracles) {
        for (uint i = 0; i < _oracles.length; i++) {
            oracles.push(AggregatorV3Interface(_oracles[i]));
        }
    }

    function getMedianPrice() public view returns (uint256) {
        uint256[] memory prices = new uint256[](oracles.length);

        for (uint i = 0; i < oracles.length; i++) {
            (,int256 price,,,) = oracles[i].latestRoundData();
            prices[i] = uint256(price);
        }

        // Sort and get median
        return getMedian(prices);
    }

    function getMedian(uint256[] memory values) internal pure returns (uint256) {
        // Bubble sort
        for (uint i = 0; i < values.length; i++) {
            for (uint j = i + 1; j < values.length; j++) {
                if (values[i] > values[j]) {
                    uint256 temp = values[i];
                    values[i] = values[j];
                    values[j] = temp;
                }
            }
        }

        // Return median
        if (values.length % 2 == 0) {
            return (values[values.length / 2 - 1] + values[values.length / 2]) / 2;
        } else {
            return values[values.length / 2];
        }
    }
}
```

## PyTh Oracle Integration

```solidity
pragma solidity ^0.8.9;

import "@pythnetwork/pyth-sdk-solidity/IPyth.sol";
import "@pythnetwork/pyth-sdk-solidity/PythStructs.sol";

contract PythPriceExample {
    IPyth public pyth;
    bytes32 public ethPriceId = 0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace;

    constructor(address _pyth) {
        pyth = IPyth(_pyth);
    }

    function updatePrice(bytes[] calldata priceUpdateData) public payable {
        // Update price and pay fee
        uint fee = pyth.getUpdateFee(priceUpdateData);
        pyth.updatePriceFeeds{value: fee}(priceUpdateData);
    }

    function getPrice() public view returns (PythStructs.Price memory price) {
        price = pyth.getPrice(ethPriceId);
    }

    function getValidPrice() public view returns (uint256) {
        PythStructs.Price memory price = pyth.getPrice(ethPriceId);

        if (price.price < 0) {
            revert("Negative price");
        }

        // Adjust to 18 decimals
        uint8 exponent = 18 + uint8(int8(-price.expo));
        return uint256(int256(price.price)) * (10 ** uint256(exponent));
    }
}
```

## Fallback Oracles

```solidity
contract FallbackOracle {
    AggregatorV3Interface public primaryFeed;
    AggregatorV3Interface public fallbackFeed;
    uint256 constant STALENESS_THRESHOLD = 1 hours;

    function getPrice() public view returns (uint256) {
        try this.getPrimaryPrice() returns (uint256 price) {
            return price;
        } catch {
            // Use fallback
            return getFallbackPrice();
        }
    }

    function getPrimaryPrice() external view returns (uint256) {
        (,int256 price,, uint256 updatedAt,) = primaryFeed.latestRoundData();

        require(price > 0, "Invalid primary price");
        require(
            block.timestamp - updatedAt < STALENESS_THRESHOLD,
            "Primary feed too stale"
        );

        return uint256(price);
    }

    function getFallbackPrice() internal view returns (uint256) {
        (,int256 price,, uint256 updatedAt,) = fallbackFeed.latestRoundData();

        require(price > 0, "Invalid fallback price");
        require(
            block.timestamp - updatedAt < STALENESS_THRESHOLD * 2,
            "Fallback feed too stale"
        );

        return uint256(price);
    }
}
```

## Testing Oracle Calls

```javascript
describe("Oracle Integration", function() {
  it("Should get latest price", async function() {
    const price = await oracle.getLatestPrice();
    expect(price).to.be.gt(0);
  });

  it("Should reject stale price", async function() {
    // Mock time to simulate stale price
    await ethers.provider.send("hardhat_mine", ["0x3000"]); // Mine blocks

    await expect(oracle.getLatestPrice())
      .to.be.revertedWith("Price too stale");
  });

  it("Should use fallback on primary failure", async function() {
    // Mock primary feed to return 0
    await primaryFeed.setPrice(0);

    const price = await oracle.getPrice();
    expect(price).to.be.gt(0); // Uses fallback
  });
});
```

---

**Key Takeaways**:
- Chainlink most trusted oracle
- Check staleness and negative prices
- Use TWAP for Uniswap prices
- Aggregate multiple sources
- Implement fallback mechanisms
- Test oracle failure scenarios
