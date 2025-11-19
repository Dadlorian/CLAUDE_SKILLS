# Tokenomics Design Guide

## Token Utility Models

### 1. Governance Token
- Voting rights on protocol decisions
- Example: UNI, COMP, AAVE

### 2. Fee Accrual Token
- Share of protocol fees
- Example: MKR, GMX

### 3. Staking/Utility Token
- Stake for rewards or access
- Example: SNX, CRV

### 4. Rebase Token
- Supply adjusts to maintain peg
- Example: AMPL, OHM

## Token Distribution

### Typical Allocation
- Team/Founders: 15-25% (4-year vest, 1-year cliff)
- Investors: 15-25% (2-4 year vest)
- Treasury: 20-40%
- Community: 20-40% (liquidity mining, airdrops)
- Advisors: 2-5%

### Vesting Schedule
```solidity
contract TokenVesting {
    uint public cliff = 365 days;
    uint public duration = 4 * 365 days;
    uint public start;

    function vestedAmount() public view returns (uint) {
        if (block.timestamp < start + cliff) return 0;
        if (block.timestamp >= start + duration) return totalAmount;

        return totalAmount * (block.timestamp - start) / duration;
    }
}
```

## Inflation/Emission

### Fixed Supply
- Bitcoin-style: No new minting
- All tokens released at launch

### Deflationary
- Burn mechanisms reduce supply
- Example: ETH post-merge, BNB

### Inflationary
- New tokens minted over time
- Decreasing schedule common

```solidity
// Halving schedule
uint public constant INITIAL_REWARD = 100e18;
uint public constant HALVING_PERIOD = 365 days;

function getCurrentReward() public view returns (uint) {
    uint halvings = (block.timestamp - startTime) / HALVING_PERIOD;
    return INITIAL_REWARD / (2 ** halvings);
}
```

## Fee Models

### Trading Fees
- 0.3% standard (Uniswap V2)
- Dynamic fees (Uniswap V3)

### Protocol Fees
- % of trading fees to treasury
- Fee switch governance

## Incentive Alignment

### Liquidity Mining
```solidity
rewardPerSecond = totalRewards / rewardDuration
userReward = (userLiquidity / totalLiquidity) * rewardPerSecond * timeElapsed
```

### Vote Escrow (ve)
- Lock tokens for voting power
- Longer lock = more power
- Example: Curve's veCRV

```solidity
votingPower = amount * (lockTime / MAX_LOCK_TIME)
```

## Anti-Gaming Mechanisms

### Time Locks
```solidity
mapping(address => uint) public lastAction;

modifier rateLimited() {
    require(block.timestamp > lastAction[msg.sender] + 1 days);
    lastAction[msg.sender] = block.timestamp;
    _;
}
```

### Snapshot Voting
- Voting power at specific block
- Prevents flash loan attacks

## Launch Strategies

### Fair Launch
- No pre-mine
- Community distribution
- Example: YFI

### Liquidity Bootstrap Pool (LBP)
- Weighted pools (Balancer)
- Price discovery mechanism

### Bonding Curves
- Price increases with supply
- Automated price discovery

## Token Security

### Supply Caps
```solidity
uint public constant MAX_SUPPLY = 1_000_000_000e18;

function mint(address to, uint amount) external {
    require(totalSupply() + amount <= MAX_SUPPLY);
    _mint(to, amount);
}
```

### Controlled Inflation
- Governance-controlled
- Gradual unlock schedules
- Emergency pause capabilities

## Tokenomics Checklist
- [ ] Clear utility defined
- [ ] Fair distribution
- [ ] Vesting schedules for team/investors
- [ ] Sustainable emission rate
- [ ] Aligned incentives
- [ ] Anti-gaming measures
- [ ] Supply cap (if applicable)
- [ ] Fee model sustainable
- [ ] Value accrual mechanism clear
