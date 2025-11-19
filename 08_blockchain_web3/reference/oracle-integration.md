# Oracle Integration Guide

## Chainlink Price Feeds

```solidity
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;

    constructor() {
        priceFeed = AggregatorV3Interface(0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419); // ETH/USD
    }

    function getLatestPrice() public view returns (int) {
        (
            uint80 roundId,
            int price,
            uint startedAt,
            uint updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        require(price > 0, "Invalid price");
        require(updatedAt >= block.timestamp - 3600, "Stale price");
        require(answeredInRound >= roundId, "Stale round");

        return price;
    }
}
```

## Uniswap V3 TWAP Oracle

```solidity
uint32[] memory secondsAgos = new uint32[](2);
secondsAgos[0] = 1800; // 30 minutes ago
secondsAgos[1] = 0;    // now

(int56[] memory tickCumulatives, ) = IUniswapV3Pool(pool).observe(secondsAgos);

int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];
int24 arithmeticMeanTick = int24(tickCumulativesDelta / 1800);

uint256 quoteAmount = OracleLibrary.getQuoteAtTick(
    arithmeticMeanTick,
    baseAmount,
    baseToken,
    quoteToken
);
```

## Oracle Security Checklist
- [ ] Staleness checks
- [ ] Price deviation limits
- [ ] Multiple oracle sources
- [ ] Fallback mechanisms
- [ ] Circuit breakers
