# ETF Selection and Evaluation

## ETF Market Overview

The ETF market has grown dramatically with over 3,000 US-listed ETFs managing over $8 trillion in assets. This growth provides excellent tools for portfolio construction but also creates selection challenges.

## Core ETF Categories for Robo-Advisors

### Broad Market Equity ETFs

**Large-Cap US Equity**:
- Ticker: SPY, VOO, IVV
- Expense Ratio: 0.03-0.08%
- Holdings: ~500 large-cap US stocks
- Tracking: S&P 500 Index
- Usage: Core equity holding

**Total US Market**:
- Ticker: VTI, SCHB
- Expense Ratio: 0.03-0.05%
- Holdings: ~3,500 all US stocks
- Tracking: Total US market
- Usage: Maximum US diversification

**Mid-Cap ETFs**:
- Ticker: VO, IJH, SCHM
- Expense Ratio: 0.04-0.05%
- Holdings: Mid-cap US stocks
- Tracking: Various mid-cap indices
- Usage: Growth exposure

**Small-Cap ETFs**:
- Ticker: VB, IJR, SCHA
- Expense Ratio: 0.05-0.07%
- Holdings: Small-cap US stocks
- Tracking: Russell 2000 or similar
- Usage: Growth and diversification

### International Equity ETFs

**Developed Markets**:
- Ticker: VEA, VXUS (ex-US portion), EFA
- Expense Ratio: 0.05-0.08%
- Holdings: ~1,500+ developed market stocks
- Coverage: Europe, Japan, Australia, etc.
- Usage: International diversification

**Emerging Markets**:
- Ticker: VWO, EEM, IEMG
- Expense Ratio: 0.08-0.40%
- Holdings: ~1,500+ emerging market stocks
- Coverage: China, India, Brazil, etc.
- Usage: Higher growth exposure

**Single-Country ETFs**:
- Various tickers (EWJ for Japan, EWU for UK, etc.)
- Expense Ratio: 0.40-0.70%
- Holdings: Country-specific stocks
- Usage: Tactical positioning, concentrated bets

### Fixed Income ETFs

**US Treasury ETFs**:
- Short-Term: SHV, VGSH (3-10 year equivalent)
- Intermediate: BND, VBTLX (5-10 year)
- Long-Term: BLV (15+ year)
- Expense Ratio: 0.03-0.06%
- Usage: Interest rate risk management

**Investment-Grade Corporate Bonds**:
- Ticker: LQD, VCIT, SCHJ
- Expense Ratio: 0.04-0.07%
- Holdings: Company bonds rated BBB or higher
- Duration: ~6-8 years
- Usage: Yield enhancement, credit exposure

**High-Yield (Junk) Bonds**:
- Ticker: HYG, ANGL, SCHB
- Expense Ratio: 0.43-0.50%
- Holdings: Bonds rated BB or lower
- Duration: ~4-5 years
- Usage: Higher yield, higher risk

**Municipal Bonds**:
- Ticker: MUB, VWLUX (taxable equivalent)
- Expense Ratio: 0.04-0.05%
- Tax: Federal tax-exempt interest
- Yield: 2-4% tax-free
- Usage: Taxable accounts, high-tax brackets

**International Bonds**:
- Ticker: BXMX, IAGG
- Expense Ratio: 0.09-0.19%
- Holdings: Global fixed income
- Currency Risk: Yes (unless hedged)
- Usage: Diversification, currency exposure

### Real Estate and Commodities

**Real Estate (REITs)**:
- Ticker: VNQ, SCHH, IYR
- Expense Ratio: 0.09-0.12%
- Holdings: US real estate companies
- Dividend Yield: 3-4%
- Usage: Inflation hedge, income

**International Real Estate**:
- Ticker: VNQI, ICVX
- Expense Ratio: 0.11-0.35%
- Holdings: International property
- Usage: Global diversification

**Commodity ETFs**:
- Gold: GLD, IAU, SGOL
- Oil: USO, USOI
- Natural Gas: UNG
- Agriculture: DBA, USAG
- Expense Ratio: 0.17-0.93%
- Usage: Inflation protection, portfolio diversification

### Factor/Smart Beta ETFs

**Value ETFs**:
- Ticker: VTV, SCHV, IUVV
- Selection: Cheap stocks (low P/E, P/B ratio)
- Expense Ratio: 0.04-0.08%
- Usage: Tactical value exposure

**Growth ETFs**:
- Ticker: VUG, SCHG, IGW
- Selection: High growth stocks
- Expense Ratio: 0.04-0.08%
- Usage: Growth portfolio exposure

**Dividend ETFs**:
- Ticker: VYM, SCHD, DGRO
- Selection: Dividend-paying stocks
- Expense Ratio: 0.06-0.08%
- Yield: 2-3%
- Usage: Income generation

**Quality ETFs**:
- Ticker: QUAL, SCHQ
- Selection: High profitability, low debt
- Expense Ratio: 0.13-0.20%
- Usage: Quality portfolio segment

**Low Volatility ETFs**:
- Ticker: SPLV, SCHP, LVOL
- Selection: Low beta stocks
- Expense Ratio: 0.16-0.20%
- Usage: Risk reduction

## ETF Selection Criteria

### 1. Expense Ratio (TER)

**Industry Benchmarks**:
- Equity Index ETFs: 0.03-0.10%
- Fixed Income ETFs: 0.04-0.20%
- Alternative ETFs: 0.20-0.50%
- Actively Managed ETFs: 0.40-1.50%

**Impact Analysis**:
```
Expense Impact on 30-Year Return:
Principal: $100,000
Annual Return: 7%
0.10% Fee: $1,689,000 final value (-$3,000)
0.50% Fee: $1,679,000 final value (-$13,000)
1.00% Fee: $1,670,000 final value (-$22,000)
```

**Recommendation**: Prioritize lowest cost for indexing, quality matters more for active management.

### 2. Assets Under Management (AUM)

**Relevance**:
- **Minimum Threshold**: $50 million (viability)
- **Sweet Spot**: $500 million+ (liquid, stable)
- **Less Important**: Size for established providers (Vanguard, iShares, Schwab)

**Risks of Small ETFs**:
- Closure risk
- Poor liquidity
- High bid-ask spreads
- Potential mergers

### 3. Trading Volume and Liquidity

**Metrics**:
- **Average Daily Volume**: Trades per day
- **Bid-Ask Spread**: Typical spread between buy/sell prices
- **Trading Cost**: Spread × position size

**Benchmarks**:
- Large ETFs: 10M+ daily volume, 1-2 basis point spread
- Moderate ETFs: 1-10M volume, 5-10 basis point spread
- Small ETFs: <1M volume, 20+ basis point spread

**Impact Calculation**:
```
Trade Cost = Position Size × Bid-Ask Spread / 2
Example: $100,000 × 0.0005 (5 bps) = $50 cost
```

### 4. Tracking Error

**Definition**: Deviation of ETF return from index return

**Causes**:
- Expense ratio
- Trading costs
- Cash drag (cash holdings)
- Sampling (not holding all securities)
- Market impact

**Acceptable Levels**:
- Full Replication: 0-5 basis points
- Sampling: 5-20 basis points
- Smart Beta: 20+ basis points (active choices)

**Measurement**:
```
Tracking Error = σ(ETF Return - Index Return)
Standard Deviation of excess returns
```

### 5. Tax Efficiency

**Characteristics**:
- **In-Kind Creation**: ETFs use in-kind process (avoids capital gains)
- **Lower Turnover**: Index ETFs have minimal trading
- **Tax Efficiency**: Most ETFs tax-efficient vs mutual funds
- **Dividend Yield**: Varies by fund strategy

**Tax-Loss Harvesting Friendly**:
- Multiple similar ETFs available
- Easy replacement strategies
- Wash-sale compliant alternatives

### 6. Index Methodology

**Index Selection**:
- **Market-Cap Weighted**: Standard approach (VTI, SPY)
- **Equal-Weighted**: All stocks weighted equally (RSP)
- **Fundamental-Weighted**: Weighted by financial metrics (PRF)
- **Dividend-Weighted**: Weighted by dividends paid (SCHD)

**Quality**:
- Transparent methodology
- Published rebalancing schedule
- Regular reconstitution
- Proven track record

## Robo-Advisor ETF Portfolio Model

### Core Holdings (80-90% of portfolio)

**Equities (60% example)**:
- 40% US Total Market (VTI)
- 20% International Developed (VEA)
- Rationale: Broad, low-cost, tax-efficient

**Fixed Income (40% example)**:
- 25% US Aggregate Bonds (BND)
- 10% International Bonds (BXMX)
- 5% TIPS (VTIP)
- Rationale: Diversified duration and credit exposure

### Satellite Holdings (10-20% of portfolio)

**Factor Tilts**:
- Value (VTV): 5%
- Dividend (SCHD): 5%
- Rationale: Enhanced returns, diversification

**Alternative Exposure**:
- Real Estate (VNQ): 5%
- Commodities (GSG): 5%
- Rationale: Inflation hedge, low correlation

## ETF Screening Process

### Step 1: Category Selection
Identify asset class and strategy needed (e.g., US Large-Cap Equity)

### Step 2: Filter Candidates
- Expense Ratio: <0.20% for index, <0.50% for factor
- AUM: >$100 million
- Age: Preferably >5 years old
- Volume: Average volume >500k shares/day

### Step 3: Detailed Analysis
- Tracking error vs index
- Holdings analysis (concentration, quality)
- Sharpe ratio and risk metrics
- Tax efficiency assessment

### Step 4: Comparison
- Direct comparison with 2-3 competitors
- Subtle differences matter (spreads, tax efficiency)
- Provider reputation and stability

### Step 5: Selection
- Choose lowest-cost option if comparable
- Choose best-execution option if differences exist
- Document rationale

## Common ETF Pitfalls

1. **Over-concentration**: Holding too many similar ETFs
2. **Chasing factors**: Buying factors after they outperform
3. **Ignoring costs**: Small expense ratio differences accumulate
4. **Ignoring liquidity**: Tight spreads reduce transaction costs
5. **Complexity**: Using complex strategies when simple works
6. **Tax drag**: Holding tax-inefficient funds in taxable accounts
7. **Overlap**: Inadvertent duplication across multiple ETFs

## Robo-Advisor Provider Examples

### Vanguard
- Lowest-cost options (0.03-0.05%)
- Institutional-quality products
- Multiple ETF families

### iShares (BlackRock)
- Comprehensive coverage
- Smart Beta options
- Good liquidity

### Schwab
- Competitive pricing
- Full-service provider
- Good alternatives coverage

### Direxion/Invesco
- Factor-based options
- Leveraged strategies
- Specialized products

## Emerging ETF Categories

- **Crypto ETFs**: Bitcoin, Ethereum physical and futures-based
- **ESG ETFs**: Environmental, social, governance screening
- **Thematic ETFs**: Technology, biotech, clean energy, cybersecurity
- **Active ETFs**: Manager-selected holdings in ETF wrapper
- **Synthetic ETFs**: Using derivatives for cost efficiency
