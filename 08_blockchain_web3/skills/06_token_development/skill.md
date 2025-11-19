# Token Development

## Overview
Design and implement fungible tokens, governance tokens, wrapped tokens, and complex tokenomics systems. Master token standards, economic models, and distribution mechanisms.

## Token Standards

### 1. ERC-20 (Fungible Token)
- **Standard Interface**: transfer, approve, balanceOf, etc.
- **Total Supply**: Fixed or dynamic supply
- **Decimals**: Typically 18 for Ether compatibility
- **Events**: Transfer, Approval for indexing
- **Extensions**: Burnable, Mintable, Pausable, Snapshot

### 2. ERC-777 (Advanced Fungible)
- **Hooks**: Send and receive hooks
- **Operators**: Authorized token operators
- **Granularity**: Minimum transfer amount
- **Backward Compatible**: Works with ERC-20

### 3. ERC-4626 (Tokenized Vaults)
- **Share Tokens**: Represent vault deposits
- **Asset Management**: Deposit and withdraw flows
- **Accounting**: Share price calculations
- **Standardization**: Compatible vault interface

## Tokenomics Design

### 1. Supply Models
- **Fixed Supply**: Hard cap (e.g., Bitcoin 21M)
- **Inflationary**: Continuous minting (e.g., Ethereum)
- **Deflationary**: Token burning mechanisms
- **Elastic**: Supply adjusts to maintain price peg
- **Hybrid**: Combination of models

### 2. Distribution Mechanisms
```solidity
// Linear vesting
function calculateVested(uint256 amount, uint256 start, uint256 duration)
    public view returns (uint256)
{
    if (block.timestamp < start) return 0;
    if (block.timestamp >= start + duration) return amount;

    return (amount * (block.timestamp - start)) / duration;
}

// Cliff vesting
function calculateCliffVested(
    uint256 amount,
    uint256 start,
    uint256 cliff,
    uint256 duration
) public view returns (uint256) {
    if (block.timestamp < start + cliff) return 0;
    if (block.timestamp >= start + duration) return amount;

    return (amount * (block.timestamp - start)) / duration;
}
```

### 3. Token Allocation
- **Team/Founders**: 15-25% with vesting
- **Investors**: 15-30% with vesting
- **Community**: 30-40% for liquidity mining
- **Treasury**: 10-20% for development
- **Ecosystem**: 10-20% for partnerships

## Advanced Features

### 1. Governance Tokens
```solidity
// Voting power with delegation
mapping(address => address) public delegates;
mapping(address => uint256) public numCheckpoints;
mapping(address => mapping(uint256 => Checkpoint)) public checkpoints;

struct Checkpoint {
    uint256 fromBlock;
    uint256 votes;
}

function delegate(address delegatee) external {
    address currentDelegate = delegates[msg.sender];
    delegates[msg.sender] = delegatee;

    _moveDelegates(currentDelegate, delegatee, balanceOf(msg.sender));
}

function getCurrentVotes(address account) external view returns (uint256) {
    uint256 nCheckpoints = numCheckpoints[account];
    return nCheckpoints > 0 ? checkpoints[account][nCheckpoints - 1].votes : 0;
}
```

### 2. Snapshot Mechanism
```solidity
// Balance snapshots for governance
uint256 private _currentSnapshotId;

mapping(uint256 => mapping(address => uint256)) private _accountBalanceSnapshots;
mapping(uint256 => uint256) private _totalSupplySnapshots;

function snapshot() external onlyOwner returns (uint256) {
    _currentSnapshotId++;
    return _currentSnapshotId;
}

function balanceOfAt(address account, uint256 snapshotId)
    public view returns (uint256)
{
    return _accountBalanceSnapshots[snapshotId][account];
}
```

### 3. Flash Mint
```solidity
interface IERC3156FlashBorrower {
    function onFlashLoan(
        address initiator,
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external returns (bytes32);
}

function flashLoan(
    IERC3156FlashBorrower receiver,
    address token,
    uint256 amount,
    bytes calldata data
) external returns (bool) {
    require(token == address(this), "Unsupported token");

    uint256 fee = _flashFee(amount);
    _mint(address(receiver), amount);

    require(
        receiver.onFlashLoan(msg.sender, token, amount, fee, data) ==
        keccak256("ERC3156FlashBorrower.onFlashLoan"),
        "Invalid return value"
    );

    _burn(address(receiver), amount + fee);
    return true;
}
```

## Wrapped Tokens

### 1. Wrapped ETH Pattern
```solidity
contract WETH is ERC20 {
    event Deposit(address indexed dst, uint256 wad);
    event Withdrawal(address indexed src, uint256 wad);

    constructor() ERC20("Wrapped Ether", "WETH") {}

    receive() external payable {
        deposit();
    }

    function deposit() public payable {
        _mint(msg.sender, msg.value);
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 wad) external {
        require(balanceOf(msg.sender) >= wad, "Insufficient balance");

        _burn(msg.sender, wad);
        payable(msg.sender).transfer(wad);

        emit Withdrawal(msg.sender, wad);
    }
}
```

### 2. Cross-Chain Wrapped Tokens
```solidity
// Lock on source chain
function lockTokens(uint256 amount, uint256 targetChain) external {
    token.transferFrom(msg.sender, address(this), amount);
    lockedBalances[msg.sender] += amount;

    emit TokensLocked(msg.sender, amount, targetChain);
}

// Mint on target chain (via bridge)
function mintWrapped(address to, uint256 amount, bytes calldata proof)
    external onlyBridge
{
    require(verifyProof(proof), "Invalid proof");
    wrappedToken.mint(to, amount);
}
```

## Staking & Rewards

### 1. Simple Staking
```solidity
contract TokenStaking {
    IERC20 public stakingToken;
    IERC20 public rewardToken;

    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public rewardDebt;

    uint256 public rewardPerTokenStored;
    uint256 public lastUpdateTime;
    uint256 public rewardRate = 100; // tokens per second

    function stake(uint256 amount) external {
        updateReward(msg.sender);

        stakingToken.transferFrom(msg.sender, address(this), amount);
        stakedBalance[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        updateReward(msg.sender);

        require(stakedBalance[msg.sender] >= amount, "Insufficient stake");
        stakedBalance[msg.sender] -= amount;

        stakingToken.transfer(msg.sender, amount);
    }

    function claimRewards() external {
        updateReward(msg.sender);

        uint256 reward = earned(msg.sender);
        if (reward > 0) {
            rewardDebt[msg.sender] = 0;
            rewardToken.transfer(msg.sender, reward);
        }
    }

    function updateReward(address account) internal {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;

        if (account != address(0)) {
            rewardDebt[account] = earned(account);
        }
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalStaked == 0) return rewardPerTokenStored;

        return rewardPerTokenStored +
            (((block.timestamp - lastUpdateTime) * rewardRate * 1e18) / totalStaked);
    }

    function earned(address account) public view returns (uint256) {
        return (stakedBalance[account] *
            (rewardPerToken() - rewardPerTokenStored)) / 1e18 + rewardDebt[account];
    }
}
```

### 2. Time-Locked Staking
```solidity
struct StakeInfo {
    uint256 amount;
    uint256 lockUntil;
    uint256 rewardMultiplier;
}

mapping(address => StakeInfo[]) public stakes;

function stake(uint256 amount, uint256 lockDays) external {
    require(lockDays >= 30 && lockDays <= 365, "Invalid lock period");

    uint256 multiplier = calculateMultiplier(lockDays);

    stakes[msg.sender].push(StakeInfo({
        amount: amount,
        lockUntil: block.timestamp + (lockDays * 1 days),
        rewardMultiplier: multiplier
    }));

    stakingToken.transferFrom(msg.sender, address(this), amount);
}

function calculateMultiplier(uint256 lockDays) public pure returns (uint256) {
    // 1x for 30 days, up to 3x for 365 days
    return 100 + ((lockDays - 30) * 200 / 335);
}
```

## Token Utilities

### 1. Utility Token Functions
- **Payment**: Transaction fees, service payments
- **Access**: Premium features, content access
- **Voting**: Governance participation
- **Staking**: Network security, yield farming
- **Rewards**: Incentive distribution

### 2. Burn Mechanisms
```solidity
// Fee burning
function _transfer(address from, address to, uint256 amount)
    internal virtual override
{
    uint256 burnAmount = (amount * burnFee) / 10000;
    uint256 transferAmount = amount - burnAmount;

    super._transfer(from, to, transferAmount);

    if (burnAmount > 0) {
        _burn(from, burnAmount);
    }
}

// Buyback and burn
function buybackAndBurn() external {
    uint256 ethBalance = address(this).balance;

    // Swap ETH for tokens via DEX
    address[] memory path = new address[](2);
    path[0] = router.WETH();
    path[1] = address(this);

    uint256[] memory amounts = router.swapExactETHForTokens{value: ethBalance}(
        0,
        path,
        address(this),
        block.timestamp
    );

    // Burn received tokens
    _burn(address(this), amounts[1]);
}
```

## Security Considerations

### 1. Approval Race Condition
```solidity
// Safe approve pattern
function increaseAllowance(address spender, uint256 addedValue)
    public returns (bool)
{
    _approve(msg.sender, spender, allowance(msg.sender, spender) + addedValue);
    return true;
}

function decreaseAllowance(address spender, uint256 subtractedValue)
    public returns (bool)
{
    uint256 currentAllowance = allowance(msg.sender, spender);
    require(currentAllowance >= subtractedValue, "Decreased below zero");

    _approve(msg.sender, spender, currentAllowance - subtractedValue);
    return true;
}
```

### 2. Transfer Hooks Protection
```solidity
// Prevent reentrancy in transfer
function _transfer(address from, address to, uint256 amount)
    internal virtual override nonReentrant
{
    super._transfer(from, to, amount);
}
```

## Testing

### 1. Token Tests
```javascript
describe("Token", function() {
    it("Should transfer tokens correctly", async function() {
        await token.transfer(addr1.address, 100);
        expect(await token.balanceOf(addr1.address)).to.equal(100);
    });

    it("Should handle approvals correctly", async function() {
        await token.approve(addr1.address, 100);
        expect(await token.allowance(owner.address, addr1.address)).to.equal(100);
    });

    it("Should enforce max supply", async function() {
        await expect(
            token.mint(owner.address, MAX_SUPPLY + 1)
        ).to.be.revertedWith("Exceeds max supply");
    });
});
```

## Compliance Considerations

### 1. Regulatory Compliance
- Securities law compliance
- KYC/AML requirements
- Transfer restrictions
- Accredited investor requirements

### 2. Restricted Tokens
```solidity
mapping(address => bool) public whitelist;
mapping(address => bool) public blacklist;

function _beforeTokenTransfer(address from, address to, uint256 amount)
    internal virtual override
{
    require(!blacklist[from] && !blacklist[to], "Blacklisted address");

    if (restrictedMode) {
        require(whitelist[from] || whitelist[to], "Not whitelisted");
    }

    super._beforeTokenTransfer(from, to, amount);
}
```

## Resources

### Standards
- EIP-20: Token Standard
- EIP-777: Advanced Token
- EIP-2612: Permit Extension
- EIP-4626: Tokenized Vaults
- EIP-3156: Flash Loans

### Tools
- OpenZeppelin Contracts
- Token Terminal
- DeFi Llama
- Etherscan

## Conclusion

Token development requires understanding of economic design, security patterns, and regulatory considerations. Build tokens that create sustainable value and align incentives for all participants.
